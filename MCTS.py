# -*- coding: utf-8 -*-
"""
Monte Carlo Tree Search in AlphaGo Zero style, which uses a policy-value
network to guide the tree search and evaluate the leaf nodes

"""

import numpy as np
import copy


def softmax(x):
    probs = np.exp(x - np.max(x))
    probs /= np.sum(probs)
    return probs


class TreeNode(object):
    """A node in the MCTS tree.

    Each node keeps track of its own value Q, prior probability P, and
    its visit-count-adjusted prior score u.
    """

    def __init__(self, parent, prior_p):
        self._parent = parent
        self._children = {}  # a map from action to TreeNode
        self._n_visits = 0
        self._Q = 0
        self._u = 0
        self._P = prior_p

    def expand(self, action_priors, board_temp):
        """Expand tree by creating new children.
        action_priors: a list of tuples of actions and their prior probability
            according to the policy function.
        """
        prob = action_priors
        for i in board_temp.valid_move:
            if i not in self._children:
                self._children[i] = TreeNode(self, prob[0][board_temp.decode_move(i)])

    def select(self, c_puct):
        """Select action among children that gives maximum action value Q
        plus bonus u(P).
        Return: A tuple of (action, next_node)
        """
        return max(self._children.items(),
                   key=lambda act_node: act_node[1].get_value(c_puct))

    def update(self, leaf_value):
        """Update node values from leaf evaluation.
        leaf_value: the value of subtree evaluation from the current player's
            perspective.
        """
        # Count visit.
        self._n_visits += 1
        # Update Q, a running average of values for all visits.
        self._Q += 1.0*(leaf_value - self._Q) / self._n_visits

    def update_recursive(self, leaf_value):
        """Like a call to update(), but applied recursively for all ancestors.
        """
        # If it is not root, this node's parent should be updated first.
        if self._parent:
            self._parent.update_recursive(-leaf_value)
        self.update(leaf_value)

    def get_value(self, c_puct):
        """Calculate and return the value for this node.
        It is a combination of leaf evaluations Q, and this node's prior
        adjusted for its visit count, u.
        c_puct: a number in (0, inf) controlling the relative impact of
            value Q, and prior probability P, on this node's score.
        """
        self._u = (c_puct * self._P *
                   np.sqrt(self._parent._n_visits) / (1 + self._n_visits))
        return self._Q + self._u

    def is_leaf(self):
        """Check if leaf node (i.e. no nodes below this have been expanded)."""
        return self._children == {}

    def is_root(self):
        return self._parent is None


class MCTS(object):
    """An implementation of Monte Carlo Tree Search."""

    def __init__(self, net, board):
        """
        policy_value_fn: a function that takes in a board state and outputs
            a list of (action, probability) tuples and also a score in [-1, 1]
            (i.e. the expected value of the end game score from the current
            player's perspective) for the current player.
        c_puct: a number in (0, inf) that controls how quickly exploration
            converges to the maximum-value policy. A higher value means
            relying on the prior more.
        """
        self._root = TreeNode(None, 1.0)
        self.net = net.policy_value
        self._c_puct = 5
        self._n_playout = 2000
        self.board = board
        self.all_prob = []

    def single(self,r):
        """Run a single playout from the root to the leaf, getting a value at
        the leaf and propagating it back through its parents.
        State is modified in-place, so a copy must be provided.
        """
        node = self._root
        board_temp = copy.deepcopy(self.board)
        while 1:
            if node.is_leaf():
                break
            # Greedily select next move.
            board_temp.next_move, node = node.select(self._c_puct)  # action, node =
            board_temp.move()
        board_temp.find_move()
        board_temp.not_end()
        if board_temp.not_end_number:
            net_input = board_temp.decode_board()
            action_probs, leaf_value = self.net([net_input])
            node.expand(action_probs, board_temp)
        else:
            # for end state，return the "true" leaf_value
            #board_temp.print_result(r)
            if board_temp.winner == 0:  # tie
                leaf_value = 0.0
            else:
                leaf_value = (-1.0 if board_temp.winner == self.board.current_player_start else 1.0)

        # Update value and visit count of nodes in this traversal.
        node.update_recursive(-leaf_value)

    def get_move(self, temp=1e-3):
        """Run all playouts sequentially and return the available actions and
        their corresponding probabilities.
        state: the current game state
        temp: temperature parameter in (0, 1] controls the level of exploration
        """
        move_probs = np.zeros(187)
        r=1
        for n in range(self._n_playout):
            #print('进行第%d次mcts模拟' % (r))
            # if n%100==0:
            #      print('正在进行第%d次mcts模拟' % (n))
            self.single(r)
            r+=1
        # calc the move probabilities based on visit counts at the root node
        act_visits = [[act, node._n_visits]
                       for act, node in self._root._children.items()]
        acts = []
        visits = []
        for i in range(len(act_visits)):
            acts.append(act_visits[i][0])
            visits.append(act_visits[i][1])
        probs = softmax(1.0/temp * np.log(np.array(visits) + 1e-10))
        for i in range(len(acts)):
            move_probs[self.board.decode_move(acts[i])] = probs[i]
        self.all_prob.append([self.board, move_probs])
        if self.board.player1 + self.board.player2 == 2:
            # add Dirichlet Noise for exploration (needed for
            # self-play training)
            move = np.random.choice(acts,p=0.75 * probs + 0.25 * np.random.dirichlet(0.3 * np.ones(len(probs))))
            # update the root node and reuse the search tree
            self.update_with_move()
            return move
        else:
            move = np.random.choice(acts, p=probs)
            # reset the root node
            self.update_with_move()
            return move

    def update_with_move(self):
        """Step forward in the tree, keeping everything we already know
        about the subtree.
        """
        if self.board.next_move in self._root._children:
            self._root = self._root._children[self.board.next_move]
            self._root._parent = None
        else:
            self._root = TreeNode(None, 1.0)



