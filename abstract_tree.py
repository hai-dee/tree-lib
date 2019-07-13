from abc import ABC, abstractmethod
import collections.abc

class AbstractBST(ABC, collections.abc.MutableSet):
    """An abstract base class for binary search trees.

    AbstractBST is an abstract base class that provides helper functions for
    binary search tree implementations. Helper functions always use iterative,
    rather than recursive, implementations so that stack overflows cannot occur.
    """


    class TreeNode:
        """A TreeNode represents a single Node in a Binary Search Tree.

        Attributes:
            key: The key contained by the TreeNode.
            right: The TreeNode's right child.
            left: The TreeNode's left child.
            parent: The TreeNode's parent.
        """

        def __init__(self, key, parent=None):
            """
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
            if self.left is not None and self.right is not None:
                return 2
            return 1


        def has_left_child_only(self) -> bool:
            """Returns true iff this node only has a left child."""
            return self.left is not None and self.right is None


        def has_right_child_only(self) -> bool:
            """Returns true iff this node only has a right child."""
            return self.right is not None and self.left is None


        @property
        def sibling(self) -> "TreeNode":
            """Returns this node's sibling

            Returns this node's sibling. The sibling has the same parent as
            this node. If the sibling does not exist, None is returned.

            Returns:
                A TreeNode which is this node's sibling, or None if the
                sibling does not exist.
            """
            if self.is_left_of_parent:
                return self.parent.right
            return self.parent.left


    def __init__(self):
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


    @_increment_after
    def add(self, key) -> None:
        """Implements MutableSet.add"""
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


    @_decrement_after
    def discard(self, key) -> None:
        """Implements MutableSet.discard"""
        return self._discard(key)


    def __iter__(self):
        """Iterates the tree with an in-order traversal."""
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
        """Implements MutableSet.__contains__"""
        return self.find_node(key) is not None


    def __len__(self) -> int:
        """Implements MutableSet.__len__"""
        return self._number_of_nodes


    def find_new_parent_node(self, key):
        """Returns the potential parent node for the given key.

        Args:
            key: The key for the new node we need a parent for.
        Returns:
            The TreeNode that will be the parent for the given key.
        Raises:
            KeyError: A node with the given key is already in the tree.
        """
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



    def replace_node(self, old_node: "TreeNode", new_node: "TreeNode") -> None:
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

        # Do the replacement.
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
