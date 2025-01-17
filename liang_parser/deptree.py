#!/usr/bin/env python
from __future__ import division

import sys

import gflags as flags

logs = sys.stderr

FLAGS=flags.FLAGS

flags.DEFINE_boolean("final_step", False, "final left reduce with <s>")

class DepVal(object):
    '''like PARSEVAL and BLEU, additive.'''

    __slots__ = "yes", "tot", "rootyes", "roottot", "completeyes"

    def __init__(self, yes=0, tot=1e-9, rootyes=0, roottot=1e-10, completeyes=0):
        self.yes = yes
        self.tot = tot
        self.rootyes = rootyes
        self.roottot = roottot
        self.completeyes = completeyes

    @staticmethod
    def unit(yes, tot, rootyes=False):
        ''' a single sentence '''
        return DepVal(yes, tot, int(rootyes), 1, int((yes == tot) and rootyes))
        
    def prec(self):
        return self.yes / self.tot if self.tot != 0 else 0

    def prec100(self):
        return self.prec() * 100

    def root(self):
        return self.rootyes / self.roottot if self.roottot != 0 else 0

    def complete(self):
        return self.completeyes / self.roottot if self.roottot != 0 else 0

    def nonroot(self):
        return (self.yes - self.rootyes) / (self.tot - self.roottot) if self.roottot != 0 else 0

    def __iadd__(self, other):
        self.yes += other.yes
        self.tot += other.tot
        self.rootyes += other.rootyes
        self.roottot += other.roottot
        self.completeyes += other.completeyes
        return self

    def __add__(self, other):
        return DepVal(yes=self.yes+other.yes,
                      tot=self.tot+other.tot,
                      rootyes=self.rootyes+other.rootyes,
                      roottot=self.roottot+other.roottot,
                      completeyes=self.completeyes+other.completeyes)

    def __eq__(self, other):
        return self.yes == other.yes and self.tot == other.tot

    def __cmp__(self, other):
        if isinstance(other, DepVal):
            return cmp(self.prec(), other.prec()) #TODO: use * not /
        else:
            return cmp(self.prec(), other)

    def __str__(self):
        return "{0:.2%}".format(self.prec())

    def details(self):
        return "word: %.2f%% (%d), non-root: %.2f%% (%d), root: %.2f%%, complete: %.2lf%% (%d)" \
               % (self.prec100(), self.tot, \
                  self.nonroot()*100, self.tot - self.roottot,
                  self.root()*100, self.complete()*100, self.roottot)

class DepTree(object):

    __slots__ = "headidx", "lefts", "rights", "_hash", "_str", "canonical"
    sent = None # static! shared by all (sub)trees of this sentence
    puncs = [",", ".", ":", "``", "''", "-LRB-", "-RRB-", "PU"]

    def __eq__(self, other):
        return str(self) == str(other) ## TODO: CACHE

    def __hash__(self):
        if self._hash is None:
            self._hash = hash(str(self)) # TODO: cache str
        return self._hash

    def __init__(self, index, lefts=[], rights=[]):
        self.headidx = index
        self.lefts = lefts
        self.rights = rights
        self._hash = None
        self._str = None

    def head(self):
        return self.sent[self.headidx]

    def tag(self):
        return self.head()[1]

    def word(self):
        return self.head()[0]

    def combine(self, next, action):
        ''' self and next are two consecutive elements on stack.
        self on the left, next on the right.'''
        if action == 1: # left-reduce
            return DepTree(next.headidx, [self]+next.lefts, next.rights)
        else:
            return DepTree(self.headidx, self.lefts, self.rights+[next])

    def __str__(self):
        ''' (... ... word/tag ... ...) '''

        # N.B.: string formatting is dangerous with single variable
        # "..." % var => "..." % tuple(var), because var might be list instead of tuple

        if self._str is None:
            word_tag = self.head()
            word = word_tag[0]

            return "(%s)" % " ".join([str(x) for x in self.lefts] + 
                                     ["%s/%s" % tuple(word_tag)] + 
                                     [str(x) for x in self.rights])
        return self._str

    def shortstr(self):
        ''' (... word ...) '''
        word_tag = self.head()
        word = word_tag[0]
            
        return "(%s)" % " ".join([x.shortstr() for x in self.lefts] + 
                                 [word] + 
                                 [x.shortstr() for x in self.rights])

    def wordtagpairs(self):
        ''' returns a list of word/tag pairs.'''
        return [x for y in self.lefts for x in y.wordtagpairs()] + \
               [self.head()] + \
               [x for y in self.rights for x in y.wordtagpairs()]

    @staticmethod
    def parse(line):
        line += " " # N.B.
        sent = []
        _, t = DepTree._parse(line, 0, sent)
        DepTree.sent = sent
        return t #, sent

    @staticmethod
    def _parse(line, index, sent):
        # print >> logs, "PARSING"
        # # print >> logs, "\n".join((line, str(index), sent))
        # print >> logs, line
        # print >> logs, index, type(index)
        # print >> logs, sent

        "((...) (...) w/t (...)). returns pos and tree, and carries sent out."

        assert line[index] == '(', "Invalid tree string %s at %d" % (line, index)
        index += 1
        head = None
        lefts = []
        rights = []
        while line[index] != ')':

            if line[index] == '(':
                index, t = DepTree._parse(line, index, sent)
                if head is None:
                    lefts.append(t)
                else:
                    rights.append(t)
                
            else:
                # head is here!
                rpos = min(line.find(' ', index), line.find(')', index))
                # see above N.B. (find could return -1)
                
                head = tuple(line[index:rpos].rsplit("/", 1)) # (word, tag) string pair

                headidx = len(sent)
                sent.append(head)
                index = rpos
                
            if line[index] == " ":
                index += 1

        assert line[index] == ')', "Invalid tree string %s at %d" % (line, index)
        try:
            t = DepTree(headidx, lefts, rights)
        except:
            pass
        return index+1, t  ## N.B.: +1

    def is_punc(self):
        return self.tag() in DepTree.puncs # PU for CTB

    def links(self, is_root=True):
        '''returns a mapping of mod=>head'''

        m = {}
        iampunc = self.is_punc()
        for i, sub in enumerate(self.lefts + self.rights):
            if not sub.is_punc(): ## is that right?
                m[sub.headidx] = self.headidx
            subm = sub.links(is_root=False)
            for x, y in subm.iteritems():
                m[x] = y

        # root
        if is_root and not self.is_punc():
            m[self.headidx] = -1
        
        return m                

    def evaluate(self, other):
        '''returns precision, correct, all.'''

        if other is None:
            return DepVal()
        
        a = self.links()
        b = other.links()

        yes = 0.
        for mod, head in a.iteritems():
            if head == b[mod]:
                yes += 1

        return DepVal.unit(yes, len(a), self.headidx==other.headidx)

    @staticmethod
    def compare(a, b):
        if a is not None:
            return a.evaluate(b)
        elif b is not None:
            return b.evaluate(a)
        else:
            return DepVal()

    def __len__(self):
        '''number of words'''
        return len(self.wordtagpairs())

    def seq(self, is_root=True):
        ''' returns the oracle action (0,1,2) sequence (a list) for the deptree'''
        
        s = []

        for sub in self.lefts:
            s += sub.seq(is_root=False)

        s += [0] # shift myself

        for _ in self.lefts:
            s += [1] # left, in center-outward (reverse) order

        for sub in self.rights:
            s += sub.seq(is_root=False)
            s += [2] # right, in center-outward (straight) order, so immediate reduce

        if FLAGS.final_step and is_root:
            s += [2] # final left reduce
        return s

    def replace_postags(self, tags):
        assert len(tags) == len(self.sent), tags
        DepTree.sent = zip([w for w, _ in self.sent], tags)

    @staticmethod
    def load(filename):
        for i, line in enumerate(open(filename), 1):
            yield DepTree.parse(line)

if __name__ == "__main__":

    FLAGS(sys.argv)
    
    for line in sys.stdin:
        print line,
        tree = DepTree.parse(line)
        seq = tree.seq()
        index = 0
        stack = ["<s>"]
        for action in seq:
            if action == 0:
                print "SHIFT", "%s/%s" % tree.sent[index]
                stack.append(tree.sent[index][0])
                index += 1
            else:
                right, left = stack.pop(), stack.pop()
                print "REDUCE %s %s %s" % (left,
                                           "<-" if action==1 else "->",
                                           right),                
                stack.append(left if action==2 else right)
                print "\t\tresult stack=[%s]" % " ".join(stack)
