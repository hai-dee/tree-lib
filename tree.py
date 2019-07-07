from abc import ABC, abstractmethod
from abstract_tree import AbstractBST
import collections.abc

class RedBlackTree(AbstractBST):

    class TreeNode(AbstractBST.TreeNode):

        def __init__(self, key, parent=None):
            self._is_red = True
            super().__init__(key, parent)

        @property
        def is_red(self):
            """Returns True iff this node is red."""
            return self._is_red

        @property
        def is_black(self):
            """Returns True iff this node is black."""
            return not self._is_red

        def paint_red(self):
            """Changes this node to red."""
            self._is_red = True

        def paint_black(self):
            """Changes this node to black."""
            self._is_red = False

        @property
        def left_is_red(self):
            """Returns True iff this node's left child is red.

            If the left child is not present, False is returned.
            """
            return self.left is not None and self.left.is_red

        @property
        def right_is_red(self):
            """Returns True iff this node's right child is red.

            If the right child is not present, False is returned.
            """
            return self.right is not None and self.right.is_red

        @property
        def left_is_black(self):
            """Returns True iff this node's left child is black.

            If the left child is not present, True is returned. This is because
            Red-Black Trees have implicit black leaf nodes.
            """
            return self.left is None or not self.left.is_red

        @property
        def right_is_black(self):
            """Returns True iff this node's right child is black.

            If the right child is not present, True is returned. This is because
            Red-Black Trees have implicit black leaf nodes.
            """
            return self.right is None or not self.right.is_red

        @property
        def sibling(self):
            """Returns this node's sibling.

            If it exists, the sibling node is the other node that shares the
            same parent. If the sibling node does not exist, None is returned.
            """
            if self.parent is not None:
                if self.is_left_of_parent:
                    return self.parent.right
                else:
                    return self.parent.left
            return None

        @property
        def aunt(self):
            """Returns this node's aunt.

            If it exists, the aunt node is defined to be the sibling of the
            parent node. If the aunt does not exist, None is returned.
            """
            if self.parent is not None and self.parent.parent is not None:
                if self.parent.is_left_of_parent:
                    return self.parent.parent.right
                else:
                    return self.parent.parent.left
            return None


        #Returns the black depth if its valid, otherwise returns -1
        def DEBUG_valid_black_depth(self):
            if self.left == None and self.right == None:
                if self.is_red:
                    return 1
                else:
                    return 2
            elif self.left == None:
                assert(self.is_black and self.right.is_red and (not self.right.left) and (not self.right.right))
                return 2
            elif self.right == None:
                assert(self.is_black and self.left.is_red and (not self.left.left) and (not self.left.right))
                return 2
            else:
                node_weight = 0 if self.is_red else 1
                left_weight = self.left.DEBUG_valid_black_depth()
                right_weight = self.right.DEBUG_valid_black_depth()
                assert(left_weight == right_weight)
                return node_weight + left_weight


        def DEBUG_valid_red_nodes(self):
            if self.left == None and self.right == None:
                return True
            if self.is_red:
                if self.left and self.left.is_red:
                    return False
                if self.right and self.right.is_red:
                    return False
            left = self.left.DEBUG_valid_red_nodes() if self.left else True
            right = self.right.DEBUG_valid_red_nodes() if self.right else True
            return left and right


    def _add(self, key):
        """Implements abstract_tree._add"""
        try:
            parent_node = self.find_new_parent_node(key)
        except(KeyError): # This happens if the node was already in the tree.
            return

        def restore_red_black_property(node):
            # Refactor this line
            while node.parent is not None and node.parent.is_red and node.aunt is not None and node.aunt.is_red:
                node = node.parent.parent
                node.paint_red()
                node.left.paint_black()
                node.right.paint_black()

            if node.parent is not None and node.parent.is_red:
                #Firstly, check if we are in the "bent" case. If so, "straighten" the branch.

                if node.is_left_of_parent and node.parent.is_right_of_parent:
                    node = node.parent
                    self.rotate_right(node)

                elif node.is_right_of_parent and node.parent.is_left_of_parent:
                    node = node.parent
                    self.rotate_left(node)

                #We are now guaranteed to be in the "straight case".
                node.parent.paint_black()
                node.parent.parent.paint_red()

                if node.is_left_of_parent:
                    self.rotate_right(node.parent.parent)
                else:
                    self.rotate_left(node.parent.parent)

        new_node = RedBlackTree.TreeNode(key, parent_node)
        if parent_node is None:
            self.root = new_node
        elif parent_node.key < new_node.key:
            parent_node.right = new_node
        else:
            parent_node.left = new_node
        restore_red_black_property(new_node)
        self.root.paint_black()
        return new_node


    def _discard(self, key):
        """Implements abstract_tree._discard"""

        def remove_node_with_only_one_child(node_to_remove):
            if node_to_remove.right is not None:
                replacement_node = node_to_remove.right
            else:
                replacement_node = node_to_remove.left
            self.replace_subtree(node_to_remove, replacement_node)
            replacement_node.paint_black()

        # A red leaf node can be directly removed without unbalancing the tree.
        def remove_red_leaf_node(node_to_remove):
            if node_to_remove.is_left_of_parent:
                node_to_remove.parent.left = None
            else:
                node_to_remove.parent.right = None

        # Simply removing a black leaf node from a Red Black Tree unbalances it,
        # because its parent will now have more weight on the other side. The
        # strategy used here to address the imbalance is to traverse up the
        # ancestory of the leaf node, converting the sibling to red at each step
        # so that the 2 branches of the parent are the same weight and the imbalance
        # is now at the grandparent node.
        # If at the current step there is already a red sibling, red parent, or
        # red niece (child of sibling), changing the sibling to red would
        # either violate the Red-Black property of the tree or be ineffective.
        # Instead, we can use the red relative to rebalance the tree and increase
        # the overall weight on the grandparent branch by 1, thus rebalancing it.
        # The exact strategy used to rebalance depends on which nodes are red.
        # Once an existing red relative has been used to rebalance the tree, the
        # upwards ascent terminates.
        # If the ascent reaches the root node, the tree will be balanced, with the
        # overall black weight reduced by 1.
        def remove_black_leaf_node(node_to_remove):
            # We start by ascending up the tree, balancing all subtrees that
            # do not have a red relative that can be used for balancing the
            # entire tree.
            current_node = node_to_remove
            while ( current_node != self.root and
                    current_node.parent.is_black and
                    current_node.sibling.is_black and
                    current_node.sibling.left_is_black and
                    current_node.sibling.right_is_black):
                current_node.sibling.paint_red()
                current_node = current_node.parent

            if current_node != self.root:

                # If the sibling is red, transform into a red-parent case and then
                # proceed to the niece and parent cases below.
                if current_node.sibling.is_red:
                    transform_red_sibling_to_red_parent(current_node)

                # If there are any red nieces, we'll need to rotate them up.
                if current_node.sibling.left_is_red or current_node.sibling.right_is_red:
                    rotate_red_niece(current_node)
                # Otherwise the only red node is the red parent, which we can use for
                # recoloring the tree how we need it.
                else:
                    current_node.parent.paint_black()
                    current_node.sibling.paint_red()

            # We can now safely delete the black leaf node.
            self.replace_subtree(node_to_remove, None)


        def transform_red_sibling_to_red_parent(node):
            node.sibling.paint_black()
            node.parent.paint_red()
            if node.is_left_of_parent:
                self.rotate_left(node.parent)
            else:
                self.rotate_right(node.parent)


        def rotate_red_niece(current_node):
            subtree_root_is_red = current_node.parent.is_red

            # If the path from the parent to the red niece is "bent", we need to rotate
            # the red niece up to the sibling position.
            if current_node.sibling.is_left_of_parent and not current_node.sibling.left_is_red:
                self.rotate_left(current_node.sibling)
            elif current_node.sibling.is_right_of_parent and not current_node.sibling.right_is_red:
                self.rotate_right(current_node.sibling)

            # Now we can rotate the parent node down onto the unbalanced side.
            if current_node.is_left_of_parent:
                self.rotate_left(current_node.parent)
            else:
                self.rotate_right(current_node.parent)

            # The grandparent node is now at the top of the subtree we've been
            # rotating. The subtree's root color must be the same as before. It's
            # children must always be black.
            new_subtree_root = current_node.parent.parent
            new_subtree_root.left.paint_black()
            new_subtree_root.right.paint_black()
            if subtree_root_is_red:
                new_subtree_root.paint_red()
            else:
                new_subtree_root.paint_black()

        node_to_delete = self.find_node(key)
        node_to_replace = None # We'll use this if node_to_delete has 2 children.

        # If there are 2 children, we will need to instead delete the inorder
        # successor, so that we can reinsert it in place of the node we
        # wish to delete.
        if node_to_delete.number_of_children == 2:
            node_to_replace = node_to_delete
            node_to_delete = self.in_order_successor(node_to_replace)

        # This could either be to delete the original node, or the inorder
        # successor. The inorder successor of a 2 child node can never have
        # more than one child itself in a valid BST.
        if node_to_delete.number_of_children == 1:
            remove_node_with_only_one_child(node_to_delete)
        elif node_to_delete.is_red:
            remove_red_leaf_node(node_to_delete)
        else:
            remove_black_leaf_node(node_to_delete)

        # If the node we deleted was the inorder successor, we now need to
        # re-insert it in the place of the deletion target, and then paint
        # it to be the same color as the node it replaces.
        if node_to_replace is not None:
            self.replace_node(node_to_replace, node_to_delete)
            if node_to_replace.is_red:
                node_to_delete.paint_red()
            else:
                node_to_delete.paint_black()


    def max_depth(self):
        """Returns the maximum depth of the RedBlackTree"""

        def recursive_helper(sub_root):
            if sub_root is None:
                return 0
            if sub_root.left is None and sub_root.right is None:
                return 1
            return 1 + max(recursive_helper(sub_root.left), recursive_helper(sub_root.right))

        return recursive_helper(self.root)


    def is_red_black_tree(self):
        """Returns True iff this is a valid RedBlackTree, False otherwise."""

        def tree_depth():
            if self.root:
                return self.root.DEBUG_valid_black_depth()
            else:
                return False

        def valid_red_nodes():
            if self.root:
                return self.root.DEBUG_valid_red_nodes()
            else:
                return True

        if self.root is not None and self.root.is_red:
            print("The tree is not a RB Tree because the root is currently red.")
            return False

        if not tree_depth():
            print("The tree is not a RB Tree because the number of black nodes on each root to leaf path are not identical.")
            return False

        if not valid_red_nodes():
            print("The tree is not a RB Tree because there are red nodes with red children.")
            return False

        return True
