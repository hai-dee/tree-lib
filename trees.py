from abc import ABC, abstractmethod
import collections.abc

class AbstractBST(ABC, collections.abc.MutableSet):

    """An abstract base class for binary search trees.

    AbstractBST is an abstract base class that provides helper functions for
    binary search tree implementations. Helper functions always use iterative,
    rather than recursive, implementations so that stack overflows cannot occur.
    """


    class TreeNode(object):

        """A TreeNode represents a single Node in a Binary Search Tree.

        Attributes:
            key: The key contained by the TreeNode.
            right: The TreeNode's right child.
            left: The TreeNode's left child.
            parent: The TreeNode's parent.
        """

        def __init__(self, key, parent=None):
            """Creates a new TreeNode.

            Args:
                key: The key the TreeNode should contain.
                parent (optional): The parent TreeNode the TreeNode should link
                    to. If not specified, it defaults to None.

            Returns:
                A TreeNode with the given key and parent if specified. The left
                and right attributes are set to None.
            """
            self.key = key
            self.right = None
            self.left = None
            self.parent = parent


        @property
        def is_left_of_parent(self) -> bool:
            """Returns True iff this node is the left child of its parent."""
            if self.parent is not None:
                return self.parent.left is self
            return False


        @property
        def is_right_of_parent(self) -> bool:
            """Returns True iff this node is the left child of its parent."""
            if self.parent is not None:
                return self.parent.right is self
            return False


        @property
        def number_of_children(self) -> int:
            """Returns this node's number of children.

            Returns:
                An interger that can be either 0, 1, or 2, depicting the number
                of child nodes this node has.
            """
            if self.left is None and self.right is None:
                return 0
            elif self.left is not None and self.right is not None:
                return 2
            else:
                return 1


        def has_left_child_only(self) -> bool:
            """Returns true iff this node only has a left child."""
            return self.left is not None and self.right is None


        def has_right_child_only(self) -> bool:
            """Returns true iff this node only has a right child."""
            return self.right is not None and self.left is None


        @property
        def sibbling(self) -> "TreeNode":
            """Returns this node's sibbling

            Returns this node's sibbling. The sibbling has the same parent as
            this node. If the sibbling does not exist, None is returned.

            Returns:
                A TreeNode which is this node's sibbling, or None if the
                sibbling does not exist.
            """
            if self.is_left_of_parent:
                return self.parent.right
            else: # This case will also return None if the sibbling doesn't exist.
                return self.parent.left


    def __init__(self):
        """Creates a new BST"""
        self.root = None
        self._number_of_nodes = 0


    def _decrement_after(func):
        def decrement_after_wrapper(self, *args, **kwargs):
            func(self, *args, **kwargs)
            self._number_of_nodes -= 1
        return decrement_after_wrapper


    def _increment_after(func):
        def increment_after_wrapper(self, *args, **kwargs):
            result = func(self, *args, **kwargs)
            if result is not None:
                self._number_of_nodes += 1
        return increment_after_wrapper


    @abstractmethod
    def _add(self, key) -> "TreeNode":
        """Abstract method: Adds the given key to the binary search tree.

        Args:
            key: The key to be added.

        Returns:
            The new TreeNode, or None if there was already a TreeNode present
            with the key.
        """
        pass


    @_increment_after
    def add(self, key) -> None:
        """See base class."""
        return self._add(key)


    @abstractmethod
    def _discard(self, key) -> bool:
        """Abstract method: Removes the given key from the binary search tree.

        Args:
            key: The key to be removed.

        Returns:
            A boolean specifying whether or not the key was actually in the
            tree. True if it was, and False if not.
        """
        pass


    @_decrement_after
    def discard(self, key) -> None:
        """See base class."""
        return self._discard(key)


    def __nonzero__(self) -> bool:
        """See base class."""
        return self.root is not None


    def __iter__(self):
        """See base class."""
        current_node = self.root
        stack = []
        while stack or current_node:
            if current_node:
                stack.append(current_node)
                current_node = current_node.left
            else:
                current_node = stack.pop()
                yield current_node.key
                current_node = current_node.right


    def __contains__(self, key) -> bool:
        """See base class."""
        return self.find_node(key) is not None


    def __len__(self) -> int:
        """See base class."""
        return self._number_of_nodes


    # Raises a KeyError if key is already in the tree.
    def find_new_parent_node(self, key):
        previous_node = None
        current_node = self.root
        while current_node is not None and current_node.key != key:
            previous_node = current_node
            if current_node.key < key:
                current_node = current_node.right
            else:
                current_node = current_node.left
        if current_node is not None:
            raise KeyError
        return previous_node



    # TODO: Add type annotation for orderable, and raise ValueError if the
    # key is not suitable.
    def find_node(self, key) -> "TreeNode":

        """Returns the node with given key.

        Helper function for implementations of Abstract BST that finds and
        returns the node with the given key. If no node with the key is found,
        None is returned.

        Args:
            key: An Orderable object whose node we want to find.

        Returns:
            The TreeNode containing key if it exists, otherwise None.
        """

        current_node = self.root
        while current_node and current_node.key != key:
            if current_node.key < key:
                current_node = current_node.right
            else:
                current_node = current_node.left
        return current_node



    def in_order_successor(self, node: "TreeNode") -> "TreeNode":

        """Returns the in-order successor of node.

        Helper function for implementations of Abstract BST that locates the
        inorder successor of the given node and returns it. If the given node
        is the last node in the tree (and thus has no in-order successor), None
        is returned.

        Args:
            node: The node whose in-order successor is to be returned.

        Returns:
            A TreeNode that is the in-order successor of node.

        Raises:
            TypeError: node is None.
        """

        # Check the input is valid.
        if node is None:
            raise TypeError("node is not allowed to be None.")

        # If the current node has a right child, the in-order successor will
        # be the leftmost node on the right subtree.
        if node.right is not None:
            current_node = node.right
            while current_node.left:
                current_node = current_node.left
            return current_node

        # Otherwise, the in-order successor, if it exists, will be the the
        # parent of the first ancestor who is a left child.
        else:
            current_node = node
            while current_node.parent is not None and current_node.is_right_of_parent:
                current_node = current_node.parent
            return current_node.parent


    def node_within_subtree(self, lower_node: "TreeNode", upper_node: "TreeNode") -> bool:
        """Checks whether or not lower_node is within the subtree of upper_node.

        Args:
            upper_node: The node whose subtree will be checked.
            lower_node: The node who will be looked for within the upper_node subtree.

        Returns:
            True if lower_node is within the upper_node subtree, False if not.
            If upper_node is None, False is returned. If lower_node is None,
            True is returned.
        """

        if upper_node is None:
            return False

        if lower_node is None:
            return True

        # The easiest way to do this is to simply traverse up the parent links
        # from lower_node. If it is indeed in the same tree as upper_node, then
        # at some point we'll get to upper_node. If we get to the root and
        # still haven't found it, we know it cannot be in the subtree.
        current_node = lower_node
        while current_node is not None:
            if current_node.key == upper_node.key:
                return True
            current_node = current_node.parent
        return False



    def substitute_node(self, old_node: "TreeNode", new_node: "TreeNode") -> None:

        """Substitutes new_node into the tree in place of old_node.

        Helper function for implementations of Abstract BST that allows for
        replacing one node with another. old_node is completely removed
        from the tree, with new_node taking its place. old_node's parent,
        left subtree, and right subtree all become new_node's.
        It is up to the caller to remove new_node from its old location, if it
        was already present in the tree.

        Args:
            old_node: The subtree to be replaced.
            new_node: The replacement subtree.

        Raises:
            TypeError: old_node or new_node is None.
        """

        # Check the input is valid.
        if old_node is None:
            raise TypeError("old_node is not allowed to be None.")
        if new_node is None:
            raise TypeError("new_node is not allowed to be None.")

        # Do the substitution.
        if old_node.parent is None:
            self.root = new_node
        elif old_node.is_left_of_parent:
            old_node.parent.left = new_node
        else:
            old_node.parent.right = new_node
        new_node.parent = old_node.parent
        self.replace_left_subtree(new_node, old_node.left)
        self.replace_right_subtree(new_node, old_node.right)



    def replace_subtree(self, old_subtree: "TreeNode", new_subtree: "TreeNode") -> None:

        """Replaces old_subtree with new_subtree.

        Helper function for implementations of Abstract BST that allows for
        replacing old_subtree with new_subtree. old_subtree's parent will
        instead link to new_subtree. If old_subtree was the tree root,
        new_subtree will become the tree root. If new_subtree is already
        elsewhere in the BST, it will be removed from the old location.
        old_subtree's parent link will also be severed.

        Args:
            old_subtree: The subtree to be replaced.
            new_subtree: The replacement subtree.

        Raises:
            TypeError: old_subtree is None.
            ValueError: old_subtree is within new_subtree.
        """

        # Check the input is valid -- we can't replace an empty subtree.
        if old_subtree is None:
            raise TypeError("old_subtree is not allowed to be None.")

        # This case is not invalid, but we also don't need to do anything in it.
        if new_subtree == old_subtree:
            return

        # Ensure new_subtree is not an ancestor of old_subtree.
        current_subtree = old_subtree.parent
        while current_subtree is not None:
            if current_subtree == new_subtree:
                raise ValueError("old_subtree is not allowed to be within new_subtree.")
            current_subtree = current_subtree.parent

        # new_subtree's parent side info has to be recorded before manipulating
        # the tree, as otherwise the algorithm breaks in the case of new_subtree
        # and old_subtree sharing a parent.
        if new_subtree is not None:
            new_subtree_was_left_of_parent = new_subtree.is_left_of_parent

        # Do the replacement.
        if old_subtree.parent is None:
            self.root = new_subtree
        else:
            if old_subtree.is_left_of_parent:
                old_subtree.parent.left = new_subtree
            else:
                old_subtree.parent.right = new_subtree
        if new_subtree is not None:

            # If new_subtree was previously in the tree, it needs to removed
            # from the old location.
            if new_subtree.parent is not None:
                if new_subtree_was_left_of_parent:
                    new_subtree.parent.left = None
                else:
                    new_subtree.parent.right = None

            new_subtree.parent = old_subtree.parent
        old_subtree.parent = None



    def replace_right_subtree(self, parent: "TreeNode", new_subtree: "TreeNode") -> None:

        """Replaces the right subtree of parent with new_subtree.

        Helper function for implementations of Abstract BST that allows
        for replacing the right subtree of a given node with a different subtree.

        Args:
            parent: The node whose right subtree is to be replaced.
            new_subtree: The replacement subtree.

        Raises:
            TypeError: parent is None.
        """

        # Check the input is valid.
        if parent is None:
            raise TypeError("parent is not allowed to be None.")

        # If new_subtree is already in the tree, its ingoing link from its
        # parent needs to be severed.
        if new_subtree is not None and new_subtree.parent is not None:
            if new_subtree.is_left_of_parent:
                new_subtree.parent.left = None
            else:
                new_subtree.parent.right = None

        # The old subtree's outgoing parent link needs to be severed.
        if parent.right is not None:
            parent.right.parent = None

        # Do the replacement.
        parent.right = new_subtree
        if new_subtree is not None:
            new_subtree.parent = parent



    def replace_left_subtree(self, parent: "TreeNode", new_subtree: "TreeNode") -> None:

        """Replaces the left subtree of parent with new_subtree.

        Helper function for implementations of Abstract BST that allows
        for replacing the left subtree of a given node with a different subtree.

        Args:
            parent: The node whose left subtree is to be replaced.
            new_subtree: The replacement subtree.

        Raises:
            TypeError: parent is None.
        """

        # Check the input is valid.
        if parent is None:
            raise TypeError("parent is not allowed to be None.")

        # If new_subtree is already in the tree, its ingoing link from its
        # parent needs to be severed.
        if new_subtree is not None and new_subtree.parent is not None:
            if new_subtree.is_left_of_parent:
                new_subtree.parent.left = None
            else:
                new_subtree.parent.right = None

        # The old subtree's outgoing parent link needs to be severed.
        if parent.left is not None:
            parent.left.parent = None

        # Do the replacement.
        parent.left = new_subtree
        if new_subtree is not None:
            new_subtree.parent = parent



    def rotate_left(self, node_to_rotate: "TreeNode") -> None:

        """Rotates the given node down one level to the left.

        Helper function for self-balancing implementations of Abstract
        BST. Takes a node that has a right child, and modifies the tree such
        that the node is now the left child of its original right child, and
        then moves other branches so that the tree remains valid.

        Args:
            node_to_rotate: a node with a right child.

        Raises:
            TypeError: node_to_rotate is None
            ValueError: node_to_rotate has no right child.
        """

        # Check the input is valid.
        if node_to_rotate is None:
            raise TypeError("node_to_rotate cannot be None")
        if node_to_rotate.right is None:
            raise ValueError("node_to_rotate must have a right child.")

        # Do the rotation.
        right_child = node_to_rotate.right
        self.replace_subtree(node_to_rotate, right_child)
        self.replace_right_subtree(node_to_rotate, right_child.left)
        self.replace_left_subtree(right_child, node_to_rotate)



    def rotate_right(self, node_to_rotate: "TreeNode") -> None:

        """Rotates the given node down one level to the right.

        Helper function for self-balancing implementations of Abstract
        BST. Takes a node that has a left child, and modifies the tree such
        that the node is now the right child of its original left child, and
        then moves other branches so that the tree remains valid.

        Args:
            node_to_rotate: a node with a left child.

        Raises:
            TypeError: node_to_rotate is None.
            ValueError: node_to_rotate has no left child.
        """

        # Check the input is valid.
        if node_to_rotate is None:
            raise TypeError("node_to_rotate cannot be None")
        if node_to_rotate.left is None:
            raise ValueError("node_to_rotate must have a left child.")

        # Do the rotation.
        left_child = node_to_rotate.left
        self.replace_subtree(node_to_rotate, left_child)
        self.replace_left_subtree(node_to_rotate, left_child.right)
        self.replace_right_subtree(left_child, node_to_rotate)


class VanillaBST(AbstractBST):

    """A binary search tree without balancing.

    A VanillaBST is the most basic implementation of AbstractBST, lacking
    any self balancing functionality. Add and discard methods work using
    text book approaches. New nodes are inserted as leaf nodes.
    """

    def _add(self, key):
        """See base class."""
        try:
            if not self: #This is the new "true root" node.
                new_node = VanillaBST.TreeNode(key, None)
                self.root = new_node
            else:
                parent_node = self.find_new_parent_node(key)
                new_node = VanillaBST.TreeNode(key, parent_node)
                if parent_node.key < new_node.key:
                    parent_node.right = new_node
                else:
                    parent_node.left = new_node
            return new_node
        except:
            return None

    def _discard(self, key):
        """See base class."""
        target_node = self.find_node(key)
        if target_node.left is None: # There is, at most, a right child.
            self.replace_subtree(target_node, target_node.right)
        elif target_node.right is None: # There are no children.
            self.replace_subtree(target_node, target_node.left)
        else: # There are two children
            successor = self.in_order_successor(target_node)
            if successor.parent != target_node:
                self.replace_subtree(successor, successor.right)
                self.replace_right_subtree(successor, target_node.right)
            self.replace_subtree(target_node, successor)
            self.replace_left_subtree(successor, target_node.left)


class RedBlackTree(AbstractBST):

    CONST_RED = True
    CONST_BLACK = False

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
        def sibbling(self):
            """Returns this node's sibbling.

            If it exists, the sibbling node is the other node that shares the
            same parent. If the sibbling node does not exist, None is returned.
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

            If it exists, the aunt node is defined to be the sibbling of the
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
                    print("oops, self is red and so is self left")
                    return False
                if self.right and self.right.is_red:
                    print("oops self is red and so is self right")
                    return False
            left = self.left.DEBUG_valid_red_nodes() if self.left else True
            right = self.right.DEBUG_valid_red_nodes() if self.right else True
            return left and right

        def DEBUG_black_leaf_node(self):
            return self.is_black and self.left is None and self.right is None

        def DEBUG_valid_parent_links(self):
            if self.parent is None:
                return True

            if self.parent.left != self and self.parent.right != self:
                return False
            elif self.parent.left == self and self.parent.right == self:
                raise AssertionError("Something has gone VERY wrong!")
            else:
                left_is_valid = self.left.DEBUG_valid_parent_links() if self.left else True
                right_is_valid = self.right.DEBUG_valid_parent_links() if self.right else True
                return left_is_valid and right_is_valid

    def DEBUG_tree_depth(self):
        if self.root:
            return self.root.DEBUG_valid_black_depth()
        else:
            return False

    def DEBUG_valid_parent_links(self):
        if self.root:
            return self.root.DEBUG_valid_parent_links()
        else:
            return True

    def DEBUG_find_black_leaf_nodes(self):
        black_leaves = []
        for node in self:
            if node.DEBUG_black_leaf_node():
                black_leaves.append(node)
        return black_leaves

    def DEBUG_valid_red_nodes(self):
        if self.root:
            return self.root.DEBUG_valid_red_nodes()
        else:
            return True

    def _add(self, key):
        """See base class."""
        try:
            parent_node = self.find_new_parent_node(key)
        except(KeyError): # This happens if the node was already in the tree.
            return
        new_node = RedBlackTree.TreeNode(key, parent_node)
        if parent_node is None:
            self.root = new_node
        elif parent_node.key < new_node.key:
            parent_node.right = new_node
        else:
            parent_node.left = new_node
        self._restore_red_black_property(new_node)
        self.root.paint_black()
        return new_node

    def _restore_red_black_property(self, node):
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

    def _discard(self, key):

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
            self._remove_one_child_node(node_to_delete)
        elif node_to_delete.is_red:
            self._remove_red_leaf_node(node_to_delete)
        else:
            self._remove_black_leaf_node(node_to_delete)

        # If the node we deleted was the inorder successor, we now need to
        # re-insert it in the place of the deletion target, and then paint
        # it to be the same color as the node it replaces.
        if node_to_replace is not None:
            self.substitute_node(node_to_replace, node_to_delete)
            if node_to_replace.is_red:
                node_to_delete.paint_red()
            else:
                node_to_delete.paint_black()

    # The only possible way a node in a Red Black Tree can have only one child
    # is if it is a black node, and the child is red. Moving the red child up
    # and painting it black will mainain tree balance.
    def _remove_one_child_node(self, node_to_remove):
        """Removes the given node that has one child

        Takes a node that has a single child and deletes it. If the
        tree was initially a valid Red-Black tree, it will remain a valid
        Red-Black tree.

        Args:
            node_to_remove: A node with one child.

        Raises:
            ValueError: node_to_remove doesn't exist, has 2 children, or has 0
                children.
        """
        if node_to_remove is None:
            raise ValueError("node_to_remove does not exist")
        if node_to_remove.number_of_children != 1:
            raise ValueError("node_to_remove should have exactly 1 child.")

        if node_to_remove.right is not None:
            replacement_node = node_to_remove.right
        else:
            replacement_node = node_to_remove.left
        self.replace_subtree(node_to_remove, replacement_node)
        replacement_node.paint_black()

    # A red leaf node can be directly removed without unbalancing the tree.
    def _remove_red_leaf_node(self, node_to_remove):
        """Removes the given red leaf node.

        Takes a red leaf node and deletes it. If the tree was initially a
        valid Red-Black tree, it will remain a valid Red-Black tree.

        Args:
            node_to_remove: A red leaf node.

        Raises:
            ValueError: node_to_remove doesn't exist or isn't a red leaf node.
        """
        if node_to_remove is None:
            raise ValueError("node_to_remove does not exist.")
        if node_to_remove.number_of_children != 0 or node_to_remove.is_black:
            raise ValueError("node_to_remove must be a red leaf node.")

        if node_to_remove.is_left_of_parent:
            node_to_remove.parent.left = None
        else:
            node_to_remove.parent.right = None

    # Simply removing a black leaf node from a Red Black Tree unbalances it,
    # because its parent will now have more weight on the other side. The
    # strategy used here to address the imbalance is to traverse up the
    # ancestory of the leaf node, converting the sibbling to red at each step
    # so that the 2 branches of the parent are the same weight and the imbalance
    # is now at the grandparent node.
    # If at the current step there is already a red sibbling, red parent, or
    # red niece (child of sibbling), changing the sibbling to red would
    # either violate the Red-Black property of the tree or be ineffective.
    # Instead, we can use the red relative to rebalance the tree and increase
    # the overall weight on the grandparent branch by 1, thus rebalancing it.
    # The exact strategy used to rebalance depends on which nodes are red.
    # Once an existing red relative has been used to rebalance the tree, the
    # upwards ascent terminates.
    # If the ascent reaches the root node, the tree will be balanced, with the
    # overall black weight reduced by 1.
    def _remove_black_leaf_node(self, node_to_remove):
        """Helper method for deletion.

        Takes a black leaf node and deletes it. If the tree was initially a
        valid Red-Black tree, it will remain a valid Red-Black tree.

        Args:
            node: A black leaf node.

        Raises:
            ValueError: node_to_remove doesn't exist or isn't a black leaf node.
        """
        if node_to_remove is None:
            raise ValueError("node_to_remove does not exist.")
        if node_to_remove.number_of_children != 0 or node_to_remove.is_red:
            raise ValueError("node_to_remove must be a black leaf node.")

        # We start by ascending up the tree, balancing all subtrees that
        # do not have a red relative that can be used for balancing the
        # entire tree.
        current_node = node_to_remove
        while ( current_node != self.root and
                current_node.parent.is_black and
                current_node.sibbling.is_black and
                current_node.sibbling.left_is_black and
                current_node.sibbling.right_is_black):
            current_node.sibbling.paint_red()
            current_node = current_node.parent

        if current_node != self.root:

            # If the sibbling is red, transform into a red-parent case and then
            # proceed to the niece and parent cases below.
            if current_node.sibbling.is_red:
                self._transform_red_sibbling_to_red_parent(current_node)

            # If there are any red nieces, we'll need to rotate them up.
            if current_node.sibbling.left_is_red or current_node.sibbling.right_is_red:
                self._rotate_red_niece(current_node)
            # Otherwise the only red node is the red parent, which we can use for
            # recoloring the tree how we need it.
            else:
                current_node.parent.paint_black()
                current_node.sibbling.paint_red()

        # We can now safely delete the black leaf node.
        self.replace_subtree(node_to_remove, None)

    def _transform_red_sibbling_to_red_parent(self, node):
        """Helper method for deletion.

        Takes a node that has a red sibbling, and transforms the tree so that
        it instead has a red parent. The overall black depths of the tree remain
        the same before and after the function is called and the tree is a valid
        Red-Black Tree after the method is run iff it already was before the
        method was run.

        Args:
            node: A black node with a red sibbling.

        Raises:
            ValueError: The input node doesn't exist, is red itself, or does not
                have a red sibbling.
        """
        if node is None:
            raise ValueError("node does not exist.")
        if node.is_red:
            raise ValueError("node should be black.")
        if node.sibbling is None or node.sibbling.is_black:
            raise ValueError("node should have a red sibbling.")

        node.sibbling.paint_black()
        node.parent.paint_red()
        if node.is_left_of_parent:
            self.rotate_left(node.parent)
        else:
            self.rotate_right(node.parent)

    def _rotate_red_niece(self, current_node):
        subtree_root_is_red = current_node.parent.is_red

        # If the path from the parent to the red niece is "bent", we need to rotate
        # the red niece up to the sibbling position.
        if current_node.sibbling.is_left_of_parent and not current_node.sibbling.left_is_red:
            self.rotate_left(current_node.sibbling)
        elif current_node.sibbling.is_right_of_parent and not current_node.sibbling.right_is_red:
            self.rotate_right(current_node.sibbling)

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
