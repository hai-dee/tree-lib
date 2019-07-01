from trees import AbstractBST
from trees import RedBlackTree
from trees import VanillaBST
import unittest


class ConcreteTestTree(AbstractBST):

    """A concrete implementation of AbstractBST that can be used for testing."""

    def __init__(self, root):
        self.root = root
        self._number_of_nodes = 0

    def set_number_of_nodes(self, x):
        self._number_of_nodes = x

    def _add(self):
        return NotImplemented

    def _discard(self):
        return NotImplemented

    def generate_link_description(self):
        return BinaryTreeSnapshot({self.root})


class BinaryTreeSnapshot(object):

    """An immutable snapshot of a binary subtree that is used for testing whether
    or not a tree changed in unexpected ways after a method call."""

    def __init__(self, component_roots=set(), ignore_branches=set()):
        self._links = {"parent": {}, "left": {}, "right": {}}
        for component_root in component_roots:
            for node in self.__node_generator_with_pruning(component_root, ignore_branches):
                self._links["left"][node.key] = node.left.key if node.left else None
                self._links["right"][node.key] = node.right.key if node.right else None
                self._links["parent"][node.key] = node.parent.key if node.parent else None

    def __node_generator_with_pruning(self, subroot, prune_branches):
        if subroot is not None and subroot not in prune_branches:
            yield subroot
            yield from self.__node_generator_with_pruning(subroot.left, prune_branches)
            yield from self.__node_generator_with_pruning(subroot.right, prune_branches)

    def __eq__(self, other):
        return self._links == other._links

    # TODO Tidy up the code in this function.
    def difference(self, other, ignore_overwrites=False):
        """Returns a description of how self differs from other and vice versa.

        Args:
            other: A BinaryTreeSnapshot
            ignore_overwrites: A boolean stating whether or not to ignore differences
                 in self of the form (p, x, y), where there was a difference in other
                 of the form (p, x, z).

        Returns:
            2 lists of differences, one of differences that are present in self,
            and the other of differences that are present in other. Each difference
            is a tuple in the form of (link_type, key_1, key_2) where link_type
            is the type of relationship that is difference ("parent, "left", or
            "right"), and key_1 and key_2 are the participants of the relationship,
            such that key_1 is the link_type of key_2.
        """

        self_differences = self.__single_direction_difference(other)
        other_differences = other.__single_direction_difference(self)
        if ignore_overwrites:
            self_differences_to_keep = []
            other_assignments = {(type, x) for type, x, _ in other_differences}
            for type, x, y in self_differences:
                if (type, x) not in other_assignments:
                    self_differences_to_keep.append((type, x, y))
            self_differences = self_differences_to_keep
        return self_differences, other_differences


    def __single_direction_difference(self, other):
        differences = []
        for link_type, links in self._links.items():
            for key, value in links.items():
                if key not in other._links[link_type] or other._links[link_type][key] != value:
                    differences.append((link_type, key, value))
        return differences


def make_sample_tree():

    # Because looking at ASCII art is awesome, lets take a very quick code break!

    ##########################################
    #........................................#
    #..THE BINARY TREE USED FOR TESTING......#
    #........................................#
    #....................100.................#
    #.................../...\................#
    #................./......\...............#
    #...............50........150............#
    #............./...\....../...............#
    #.........../......\..../................#
    #.........25.......75...125..............#
    #......../..\...........\................#
    #......./....\...........\...............#
    #.....12......37.........130.............#
    #............/..\...........\............#
    #........../.....\...........\...........#
    #........30.......40..........140........#
    #......./...........\......../...........#
    #....../.............\....../............#
    #....28...............45...135...........#
    #.....\............../..\....\...........#
    #......\............/....\....\..........#
    #.......29.........42.....47...137.......#
    #........................................#
    ##########################################

    nodes_to_use = {
        100: (50, 150),
        50: (25, 75),
        150: (125, None),
        25: (12, 37),
        75: (None, None),
        125: (None, 130),
        12: (None, None),
        37: (30, 40),
        130: (None, 140),
        30: (28, None),
        40: (None, 45),
        140: (135, None),
        45: (42, 47),
        135: (None, 137),
        42: (None, None),
        47: (None, None),
        137: (None, None),
        28: (None, 29),
        29: (None, None,)
    }

    node_set = {}

    for key in nodes_to_use:
        node = AbstractBST.TreeNode(key)
        node_set[key] = node

    for key, (left_key, right_key) in nodes_to_use.items():

        if left_key is not None:
            node_set[left_key].parent = node_set[key]
            node_set[key].left = node_set[left_key]

        if right_key is not None:
            node_set[right_key].parent = node_set[key]
            node_set[key].right = node_set[right_key]

    tree =  ConcreteTestTree(node_set[100])
    tree.set_number_of_nodes(len(nodes_to_use))

    return tree


class TestAbstractBSTReadOnlyMethods(unittest.TestCase):

    """This class provides unit tests for the following read only methods of AbstactBST
    1) __iter__
    2) node_within_subtree
    3) find_node
    4) find_new_parent_node
    5) in_order_successor
    6) __non_zero__
    7) __contains__
    """

    def setUp(self):

        self.tree = make_sample_tree()



    def test_non_zero_on_non_zero(self):
        self.assertTrue(self.tree, "A non empty-tree should be True.")



    def test_non_zero_on_zero(self):
        self.assertFalse(ConcreteTestTree(None), "An empty tree should be False.")


    def test_iter(self):

        expected_result = [12, 25, 28, 29, 30, 37, 40, 42, 45, 47, 50, 75, 100, 125, 130, 135, 137, 140, 150]

        got_result = list(self.tree)
        self.assertEqual(expected_result, got_result, "The iterator should return the nodes in inorder traversal order.")



    def test_node_within_subtree_on_none_lower_node(self):

        upper_key = 12

        links_before_lookup = self.tree.generate_link_description()
        result = self.tree.node_within_subtree(None, self.tree.find_node(upper_key))

        with self.subTest(lower_key=None, upper_key=upper_key):
            self.assertTrue(result, "When lower_node is None, and upper_node is a TreeNode, True should always be returned.")

        with self.subTest(lower_key=None, upper_key=upper_key):
            self.assertEqual(links_before_lookup, self.tree.generate_link_description(), "This method should not modify the tree or its structure.")



    def test_node_within_subtree_on_none_upper_node(self):

        lower_key = 12
        links_before_lookup = self.tree.generate_link_description()
        result = self.tree.node_within_subtree(self.tree.find_node(lower_key), None)

        with self.subTest(lower_key=lower_key, upper_key=None):
            self.assertFalse(result, "When lower_node is a TreeNode, and upper_node is None, False should always be returned.")

        with self.subTest(lower_key=lower_key, upper_key=None):
            self.assertEqual(links_before_lookup, self.tree.generate_link_description(), "This method should not modify the tree or its structure.")



    def test_node_within_subtree_both_args_none(self):

        links_before_lookup = self.tree.generate_link_description()
        result = self.tree.node_within_subtree(None, None)

        with self.subTest(lower_key=None, upper_key=None):
            self.assertFalse(result, "When both args are None, False should always be returned.")

        with self.subTest(lower_key=None, upper_key=None):
            self.assertEqual(links_before_lookup, self.tree.generate_link_description(), "This method should not modify the tree or its structure.")



    def test_node_within_subtree_on_valid_input(self):

        test_cases = [
            (47, 45, True),     # Is right child.
            (42, 45, True),     # Is left child.
            (130, 100, True),   # Within right subtree, and upper is root.
            (40, 50, True),     # Within left subtree.
            (42, 47, False),    # Nodes are sibblings.
            (47, 42, False),    # Nodes are sibblings (reversed).
            (50, 30, False),    # Upper is within lower's left subtree.
            (125, 135, False),  # Upper is within lower's right subtree.
            (28, 130, False),   # Only shared relative is root
            (130, 28, False),   # Only shared relative is root (reversed)
        ]

        for lower_key, upper_key, expected_result in test_cases:

            self.setUp()

            links_before_lookup = self.tree.generate_link_description()
            got_result = self.tree.node_within_subtree(self.tree.find_node(lower_key), self.tree.find_node(upper_key))

            with self.subTest(lower_key=lower_key, upper_key=upper_key):
                self.assertEqual(expected_result, got_result, "Expected {} but got {}".format(expected_result, got_result))

            with self.subTest(lower_key=lower_key, upper_key=upper_key):
                self.assertEqual(links_before_lookup, self.tree.generate_link_description(), "This method should not modify the tree or its structure.")


    def test_contains_empty_tree(self):
        empty_tree = ConcreteTestTree(None)
        self.assertFalse(12 in empty_tree, "An empty tree should return False on contains queries.")



    def test_find_new_parent_node_key_on_valid_input(self):
        # Each test case contains 2 intergers.
        # 1) The key to find a parent for.
        # 2) The expected parent key.
        test_cases = [
            (138, 137),     # Right of leaf node
            (136, 137),     # Left of leaf node
            (141, 140),     # Right of one-child node
            (134, 135),     # Left of one-child node
        ]

        for key, expected_parent_key in test_cases:

            self.setUp()

            links_before_lookup = self.tree.generate_link_description()
            got_parent = self.tree.find_new_parent_node(key)

            with self.subTest(key=key, expected_parent_key=expected_parent_key):
                self.assertIsNotNone(got_parent, "expected {} but got None.".format(expected_parent_key))
                self.assertEqual(expected_parent_key, got_parent.key, "expected {} but got {}".format(expected_parent_key, got_parent.key))

            with self.subTest(key=key):
                self.assertEqual(links_before_lookup, self.tree.generate_link_description(), "This method should not modify the tree or its structure.")



    def test_find_new_parent_node_key_error(self):

        test_cases = [
            100,    # The root node.
            37,     # 2 children, right of parent.
            50,     # 2 children, left of parent.
            42,     # Leaf node, left of parent.
            47,     # Leaf node, right of parent.
            40,     # 1 child, right of parent.
        ]

        for key in test_cases:

            self.setUp()

            with self.subTest(key=key):
                with self.assertRaises(KeyError):
                    self.tree.find_new_parent_node(key)

            self.setUp()

            with self.subTest(key=key):
                links_before_lookup = self.tree.generate_link_description()
                try:
                    self.tree.find_new_parent_node(key)
                except:
                    self.assertEqual(links_before_lookup, self.tree.generate_link_description(), "This method should not modify the tree or its structure.")



    def test_find_node_on_present_key(self):

        test_cases = [
            100,    # Root node.
            50,     # Left child of root.
            150,    # Right child of root.
            45,     # Internal node.
            40,     # Internal node.
            135,    # Internal node.
            42,     # Leaf node, is left child.
            137,    # Leaf node, is right child.
            75,     # Shallow leaf node, is right child.
            12,     # Shallow leaf node, is left child.
        ]

        for key in test_cases:

            self.setUp()

            links_before_lookup = self.tree.generate_link_description()
            found_node = self.tree.find_node(key)

            with self.subTest(key=key):
                self.assertIsNotNone(found_node, "expected {} but got None.".format(key))
                self.assertEqual(key, found_node.key, "expected {} but got {}.".format(key, found_node.key))

            with self.subTest(key=key):
                self.assertEqual(links_before_lookup, self.tree.generate_link_description(), "This method should not modify the tree or its structure.")



    def test_find_node_on_absent_key(self):

        test_cases = [101, -1, 51, 0] # Keys not in tree.

        for key in test_cases:

            self.setUp()

            links_before_lookup = self.tree.generate_link_description()
            found_node = self.tree.find_node(key)

            with self.subTest(key=key):
                self.assertIsNone(found_node, "expected None but got {}".format(found_node))

            with self.subTest(key=key):
                self.assertEqual(links_before_lookup, self.tree.generate_link_description(), "This method should not modify the tree or its structure.")



    def test_contains_on_present_key(self):
        test_cases = [
            100,    # Root node.
            50,     # Left child of root.
            150,    # Right child of root.
            45,     # Internal node.
            40,     # Internal node.
            135,    # Internal node.
            42,     # Leaf node, is left child.
            137,    # Leaf node, is right child.
            75,     # Shallow leaf node, is right child.
            12,     # Shallow leaf node, is left child.
        ]
        for key in test_cases:

            self.setUp()

            links_before_lookup = self.tree.generate_link_description()
            result = key in self.tree

            with self.subTest(key=key):
                self.assertTrue(result, "Expected True but got False.")

            with self.subTest(key=key):
                self.assertEqual(links_before_lookup, self.tree.generate_link_description(), "This method should not modify the tree or its structure.")




    def test_contains_on_absent_key(self):
        test_cases = [101, -1, 51, 0] # Keys not in tree.
        for key in test_cases:

            links_before_lookup = self.tree.generate_link_description()
            result = key in self.tree

            with self.subTest(key=key):
                self.assertFalse(result, "expected False but got True.")

            with self.subTest(key=key):
                self.assertEqual(links_before_lookup, self.tree.generate_link_description(), "This method should not modify the tree or its structure.")



    def test_find_new_parent_node_on_empty_tree(self):

        tree = ConcreteTestTree(None)
        parent_node = tree.find_new_parent_node(1)
        self.assertIsNone(parent_node, "None should be returned when the tree is empty.")






    def test_in_order_successor_on_valid_inputs(self):
        # Test cases are of the form (key, inorder_successor(key).key)
        test_cases = [
            (100, 125),     # Root node.
            (30, 37),       # Leaf node, left of parent.
            (47, 50),       # Leaf node, right of parent.
            (50, 75),       # Inorder successor is right child.
            (25, 28),       # Inorder successor is in right subtree.
        ]

        for key, expected_inorder_successor_key in test_cases:

            self.setUp()
            links_before_lookup = self.tree.generate_link_description()
            got_key = self.tree.in_order_successor(self.tree.find_node(key)).key

            with self.subTest(key_of_node=key, expected_inorder_successor_key=expected_inorder_successor_key):
                self.assertEqual(expected_inorder_successor_key, got_key, "expected {}, but got {}.".format(expected_inorder_successor_key, got_key))

            with self.subTest(key_of_node=key):
                self.assertEqual(links_before_lookup, self.tree.generate_link_description(), "This method should not modify the tree or its structure.")



    def test_in_order_successor_on_tree_maximum(self):
        self.assertIsNone(self.tree.in_order_successor(self.tree.find_node(150)), "The in-order successor of the tree maximum should be None.")



    def test_in_order_successor_on_singleton_tree(self):
        singleton_tree = ConcreteTestTree(None)
        singleton_tree.root = AbstractBST.TreeNode(1)
        self.assertIsNone(singleton_tree.in_order_successor(singleton_tree.root), "The in-order successor of the tree maximum should be None.")



    def test_inorder_successor_raises_type_error_on_None_key(self):
        with self.assertRaises(TypeError):
            self.tree.in_order_successor(None)


class TestAbstractBSTSubtreeReplacementMethods(unittest.TestCase):

    """This class provides unit tests for the following subtree replacement
    methods of AbstractBST.
    1) replace_subtree
    2) replace_left_subtree
    3) replace_right_subtree
    """

    def setUp(self):
        self.tree = make_sample_tree()


    def test_replace_subtree(self):

        test_cases = [
            # 25 is a 2 child node to the left of its parent. 125  is a 1 child node to the left of its parent. 125 is not within 25's subtree.
            [25, 125, [("parent", 25, None), ("left", 50, 125), ("left", 150, None), ("parent", 125, 50)]],
            # 42 and 47 are both leaf nodes, that share the parent 45.
            [42, 47, [("parent", 42, None), ("left", 45, 47), ("right", 45, None)]],
            # 47 and 42 are both leaf nodes, that share the parent 45.
            [47, 42, [("parent", 47, None), ("right", 45, 42), ("left", 45, None)]],
            # Replace the root node with its right child.
            [100, 150, [("parent", 150, None), ("right", 100, None)]],
            # Replace the root node with its left child.
            [100, 50, [("parent", 50, None), ("left", 100, None)]],
            # Replace a leaf node with None.
            [135, None, [("parent", 135, None), ("left", 140, None)]],
            # Replace the root node with None. No links should change.
            [100, None, []],
            # Replace a node with itself. No linkes should change.
            [37, 37, []],
        ]

        for to_replace_key, to_move_key, expected_changes in test_cases:

            self.setUp()

            with self.subTest(to_replace_key=to_replace_key, to_move_key=to_move_key, expected_changes=expected_changes):
                node_to_replace = self.tree.find_node(to_replace_key)
                if to_move_key is None:
                    node_to_move = None
                else:
                    node_to_move = self.tree.find_node(to_move_key)
                snapshot_before = BinaryTreeSnapshot({self.tree.root, node_to_move, node_to_replace})
                self.tree.replace_subtree(node_to_replace, node_to_move)
                snapshot_after = BinaryTreeSnapshot({self.tree.root, node_to_move, node_to_replace})
                missing_relations, got_changes = snapshot_before.difference(snapshot_after, ignore_overwrites=True)
                self.assertFalse(missing_relations, "These tree links should still be present in the tree.")
                self.assertEqual(set(expected_changes), set(got_changes), "Some tree links did not change as expected.")



    def test_replace_subtree_raises_type_error(self):
        with self.assertRaises(TypeError, msg="replace_subtree should raise a TypeError if old_subtree is None."):
            new_subtree_node = self.tree.find_node(12)
            self.tree.replace_subtree(None, new_subtree_node)


    def test_replace_subtree_raises_value_error(self):
        with self.assertRaises(ValueError, msg="replace_subtree should raise a ValueError if old_subtree is within new_subtree."):
            old_subtree = self.tree.find_node(37)
            new_subtree = self.tree.find_node(50)
            self.tree.replace_subtree(old_subtree, new_subtree)

    def test_replace_subtree_on_root_change(self):
        old_subtree = self.tree.find_node(100) # The root.
        new_subtree = self.tree.find_node(50)
        self.tree.replace_subtree(old_subtree, new_subtree)
        self.assertEqual(self.tree.root.key, 50, "self.root should update when the root node is changed.")


    def test_replace_left_subtree(self):

        test_cases = [
            # Replace the root's left subtree with None.
            [100, None, [('parent', 50, None), ('left', 100, None)]],
            # Replace the root's left subtree with its right subtree.
            [100, 150, [('right', 100, None), ('left', 100, 150), ('parent', 50, None)]],
            # Replace the root's left subtree with an independent subtree*.
            [100, 135, [('left', 140, None), ('parent', 135, 100), ('left', 100, 135), ('parent', 50, None)]],
            # Replace the root's left subtree with its own left subtree.
            [100, 25, [('parent', 25, 100), ('left', 100, 25), ('left', 50, None), ('parent', 50, None)]],
            # Replace a 2 child node's left leaf subtree with None.
            [45, None, [('parent', 42, None), ('left', 45, None)]],
            # Replace a 2 child's left leaf subtree with an independent subtree*.
            [45, 30, [('left', 37, None), ('parent', 42, None), ('left', 45, 30), ('parent', 30, 45)]],
            # *independent subtree means a subtree not within the subtree to be removed.
            #[],
        ]

        for parent_key, to_move_key, expected_changes in test_cases:

            self.setUp()

            parent = self.tree.find_node(parent_key)
            node_to_replace = parent.left
            if to_move_key is None:
                node_to_move = None
            else:
                node_to_move = self.tree.find_node(to_move_key)

            snapshot_before = BinaryTreeSnapshot({self.tree.root, node_to_move, node_to_replace})
            self.tree.replace_left_subtree(parent, node_to_move)
            snapshot_after = BinaryTreeSnapshot({self.tree.root, node_to_move, node_to_replace})

            with self.subTest(parent_key=parent_key, to_move_key=to_move_key, expected_changes=expected_changes):

                missing_relations, got_changes = snapshot_before.difference(snapshot_after, ignore_overwrites=True)
                self.assertFalse(missing_relations, "These tree links should still be present in the tree.")
                self.assertEqual(set(expected_changes), set(got_changes), "Some tree links did not change as expected.")

            with self.subTest(parent_key=parent_key, to_move_key=to_move_key, expected_changes=expected_changes):
                self.assertEqual(self.tree.root.key, 100, "replace_left_subtree should not change the root node.")



    def test_replace_left_subtree_raises_type_error(self):
        with self.assertRaises(TypeError, msg="replace_subtree should raise a TypeError if parent is None."):
            new_subtree_node = self.tree.find_node(12)
            self.tree.replace_left_subtree(None, new_subtree_node)



    def test_replace_right_subtree(self):

        test_cases = [
            # Replace the root's right subtree with None.
            [100, None, [('parent', 150, None), ('right', 100, None)]],
            # Replace the root's right subtree with the root's left subtree.
            [100, 50, [('left', 100, None), ('right', 100, 50), ('parent', 150, None)]],
            # Replace the root's right subtree with an independent subtree*.
            [100, 40, [('parent', 150, None), ('parent', 40, 100), ('right', 100, 40), ('right', 37, None)]],
            # Replace the root's right subtree with its own left subtree.
            [100, 125, [('parent', 125, 100), ('right', 100, 125), ('left', 150, None), ('parent', 150, None)]],
            # Replace a 2 child node's right leaf subtree with None.
            [45, None, [('parent', 47, None), ('right', 45, None)]],
            # Replace a 2 child's left leaf subtree with an independent subtree*.
            [45, 30, [('left', 37, None), ('parent', 47, None), ('right', 45, 30), ('parent', 30, 45)]],
            # *independent subtree means a subtree not within the subtree to be removed.
            #[],
        ]

        for parent_key, to_move_key, expected_changes in test_cases:

            self.setUp()

            parent = self.tree.find_node(parent_key)
            node_to_replace = parent.right
            if to_move_key is None:
                node_to_move = None
            else:
                node_to_move = self.tree.find_node(to_move_key)

            snapshot_before = BinaryTreeSnapshot({self.tree.root, node_to_move, node_to_replace})
            self.tree.replace_right_subtree(parent, node_to_move)
            snapshot_after = BinaryTreeSnapshot({self.tree.root, node_to_move, node_to_replace})

            with self.subTest(parent_key=parent_key, to_move_key=to_move_key, expected_changes=expected_changes):

                missing_relations, got_changes = snapshot_before.difference(snapshot_after, ignore_overwrites=True)
                self.assertFalse(missing_relations, "These tree links should still be present in the tree.")
                self.assertEqual(set(expected_changes), set(got_changes), "Some tree links did not change as expected.")

            with self.subTest(parent_key=parent_key, to_move_key=to_move_key, expected_changes=expected_changes):
                self.assertEqual(self.tree.root.key, 100, "replace_right_subtree should not change the root node.")



    def test_replace_right_subtree_raises_type_error(self):
        with self.assertRaises(TypeError, msg="replace_subtree should raise a TypeError if parent is None."):
            new_subtree_node = self.tree.find_node(12)
            self.tree.replace_right_subtree(None, new_subtree_node)


class TestAbstractBSTRotateMethods(unittest.TestCase):

    """This class provides unit tests for the following subtree rotationt
    methods of AbstractBST.
    1) rotate_left
    2) rotate_right
    """

    def setUp(self):
        self.tree = make_sample_tree()



    def test_rotate_left(self):

        test_cases = [
            # The root node
            [100, [("parent", 150, None), ("parent", 100, 150), ("left", 150, 100), ("right", 100, 125), ("parent", 125, 100)]],
            # Has 2 children, left of its parent, node.right.left exists.
            [25, [("left", 50, 37), ("parent", 37, 50), ("left", 37, 25), ("parent", 25, 37), ("right", 25, 30), ("parent", 30, 25)]],
            # Has 2 children, right of its parent, node.right.left is None.
            [37, [("right", 25, 40), ("parent", 40, 25), ("left", 40, 37), ("right", 37, None), ("parent", 37, 40)]],
            # Has 1 child, left of its parent, node.right.left is None.
            [125, [("left", 150, 130), ("parent", 130, 150), ("left", 130, 125), ("parent", 125, 130), ("right", 125, None)]],
            # Has 1 child, right of its parent, node.right.left exists.
            [130, [("right", 125, 140), ("parent", 140, 125), ("left", 140, 130), ("parent", 130, 140), ("right", 130, 135), ("parent", 135, 130)]],
        ]

        for key, expected_changes in test_cases:

            is_root = key == 100
            self.setUp() # Must reset the tree each time.

            snapshot_before = BinaryTreeSnapshot({self.tree.root})
            self.tree.rotate_left(self.tree.find_node(key))
            snapshot_after = BinaryTreeSnapshot({self.tree.root})
            missing_relations, got_changes = snapshot_before.difference(snapshot_after, ignore_overwrites=True)

            with self.subTest(key=key, expected_changes=expected_changes):
                self.assertFalse(missing_relations, "These tree links should still be present in the tree.")
                self.assertEqual(set(expected_changes), set(got_changes), "Some tree links did not change as expected.")

            with self.subTest(key=key, is_root=is_root):
                if is_root:
                    self.assertEqual(self.tree.root.key, 150, "When the root is rotated left, the new root should be the old root's right child.")
                else:
                    self.assertEqual(self.tree.root.key, 100, "When a node other than the root is rotated, the root should not change.")



    def test_rotate_left_type_error(self):

        with self.assertRaises(TypeError, msg="rotate_left should raise a TypeError if arg is None."):
            self.tree.rotate_left(None)



    def test_rotate_left_value_error(self):

        with self.assertRaises(ValueError, msg="rotate_left should raise a ValueError if the given node has no right child."):
            self.tree.rotate_left(self.tree.find_node(75)) # Has no children

        with self.assertRaises(ValueError, msg="rotate_left should raise a ValueError if the given node has no right child."):
            self.tree.rotate_left(self.tree.find_node(140)) # Has left child only



    def test_rotate_right(self):

        test_cases = [
            # The root node
            [100, [("parent", 50, None), ("parent", 100, 50), ("parent", 75, 100), ("right", 50, 100), ("left", 100, 75)]],
            # Has 2 children, right  of its parent, node.left.right is None.
            [45, [("right", 42, 45), ("parent", 45, 42), ("parent", 42, 40), ("left", 45, None), ("right", 40, 42)]],
            # Has 2 children, left of its parent, node.left.right exists.
            [50, [("parent", 50, 25), ("parent", 25, 100), ("left", 50, 37), ("parent", 37, 50), ("left", 100, 25), ("right", 25, 50)]],
            # Has 1 child, left of its parent, node.left.right exists.
            [30, [("left", 37, 28), ("parent", 30, 28), ("parent", 28, 37), ("left", 30, 29), ("parent", 29, 30), ("right", 28, 30)]],
        ]


        for key, expected_changes in test_cases:

            is_root = key == 100
            self.setUp() # Must reset the tree each time.

            snapshot_before = BinaryTreeSnapshot({self.tree.root})
            self.tree.rotate_right(self.tree.find_node(key))
            snapshot_after = BinaryTreeSnapshot({self.tree.root})
            missing_relations, got_changes = snapshot_before.difference(snapshot_after, ignore_overwrites=True)

            with self.subTest(key=key, expected_changes=expected_changes):
                self.assertFalse(missing_relations, "These tree links should still be present in the tree.")
                self.assertEqual(set(expected_changes), set(got_changes), "Some tree links did not change as expected.")

            with self.subTest(key=key, is_root=is_root):
                if is_root:
                    self.assertEqual(self.tree.root.key, 50, "When the root is rotated right, the new root should be the old root's left child.")
                else:
                    self.assertEqual(self.tree.root.key, 100, "When a node other than the root is rotated, the root should not change.")



    def test_rotate_right_type_error(self):

        with self.assertRaises(TypeError, msg="rotate_right should raise a TypeError if arg is None."):
            self.tree.rotate_right(None)



    def test_rotate_right_value_error(self):

        with self.assertRaises(ValueError, msg="rotate_right should raise a ValueError if the given node has no right child."):
            self.tree.rotate_right(self.tree.find_node(75)) # Has no children

        with self.assertRaises(ValueError, msg="rotate_right should raise a ValueError if the given node has no right child."):
            self.tree.rotate_right(self.tree.find_node(125)) # Has right child only


class TestAbstractBSTSubstituteMethods(unittest.TestCase):

    def setUp(self):
        self.tree = make_sample_tree()



    def test_substitue_node(self):
        test_cases = [
            # Root node smaller.
            (100, 99, [('parent', 99, None), ('parent', 50, 99), ('parent', 150, 99), ('left', 99, 50), ('right', 99, 150)]),
            # Root node bigger.
            (100, 101, [('parent', 101, None), ('parent', 50, 101), ('parent', 150, 101), ('left', 101, 50), ('right', 101, 150)]),
            # 2 children, right of parent.
            (37, 38,  [('parent', 38, 25), ('parent', 30, 38), ('parent', 40, 38), ('left', 38, 30), ('right', 25, 38), ('right', 38, 40)]),
            # 2 children, left of parent.
            (50, 51,  [('parent', 51, 100), ('parent', 25, 51), ('parent', 75, 51), ('left', 51, 25), ('right', 51, 75), ('left', 100, 51)]),
            # Leaf node, right of parent.
            (47, 46, [('parent', 46, 45), ('right', 45, 46), ('left', 46, None), ('right', 46, None)]),
            # Leaf node, left of parent.
            (42, 43, [('parent', 43, 45), ('left', 45, 43), ('left', 43, None), ('right', 43, None)]),
            # Right child only, left of parent.
            (135, 136, [('parent', 136, 140), ('left', 136, None), ('left', 140, 136), ('parent', 137, 136), ('right', 136, 137)]),
            # Left child only, right of parent.
            (140, 141, [('parent', 135, 141), ('left', 141, 135), ('right', 130, 141), ('parent', 141, 130), ('right', 141, None)]),
        ]

        for old_key, new_key, expected_changes in test_cases:

            self.setUp()

            old_node = self.tree.find_node(old_key)
            new_node = AbstractBST.TreeNode(new_key)

            snapshot_before = BinaryTreeSnapshot({self.tree.root})
            self.tree.substitute_node(old_node, new_node)
            snapshot_after = BinaryTreeSnapshot({self.tree.root})
            missing_relations, got_changes = snapshot_before.difference(snapshot_after, ignore_overwrites=True)

            # Filter out any missing relations where old_key is the first node referenced.
            # This is because we expect these facts to have disappeared.
            missing_relations = [relation for relation in missing_relations if relation[1] != old_key]

            with self.subTest(old_key=old_key, new_key=new_key, expected_changes=expected_changes):
                self.assertFalse(missing_relations, "These tree links should still be present in the tree.")
                self.assertEqual(set(expected_changes), set(got_changes), "Some tree links did not change as expected.")

            with self.subTest(old_key=old_key, new_key=new_key):
                if old_key == 100:
                    self.assertEqual(self.tree.root.key, new_key, "When the root is substituited, the root should now have new_key.")
                else:
                    self.assertEqual(self.tree.root.key, 100, "When a node other than the root is substituited, the root key should not change.")



    def test_substitute_node_type_error(self):

        test_cases = [(None, None), (12, None), (None, 12)]

        for old_key, new_key in test_cases:

            self.setUp()

            old_node = self.tree.find_node(old_key) if old_key is not None else None
            new_node = AbstractBST.TreeNode(new_key) if new_key is not None else None

            with self.subTest(old_key=old_key, new_key=new_key):
                with self.assertRaises(TypeError, msg="substitute_node should raise a TypeError if either arg is None."):
                    self.tree.substitute_node(old_node, new_node)


class TestRedBlackTree(unittest.TestCase):

    def test_add_and_remove(self):

        tree = RedBlackTree()

        keys = [1, 2, 3, 4, 5, 20, 15, 14, 13, 12, 11, 6, 7, 8, 9, 19, 18, 25, 23, 24, 22, 21, 64, 66, 67, 69, 37, 39, 70, 73, 40, 75, 42, 76, 46, 47, 49, 53, 58, 62]
        for key in keys:
            tree.add(key)
            self.assertTrue(key in tree, "Key {} should be in the tree".format(key))

        for key in keys:
            tree.remove(key)
            self.assertFalse(key in tree, "Key {} should no longer be in the tree.".format(key))


    def test_remove_on_not_present(self):
        tree = RedBlackTree()

        keys = [1, 2, 3, 4, 5, 20, 15, 14, 13, 12, 11, 6, 7, 8, 9, 19, 18, 25, 23, 24, 22, 21, 64, 66, 67, 69, 37, 39, 70, 73, 40, 75, 42, 76, 46, 47, 49, 53, 58, 62]
        for key in keys: tree.add(key)
        non_existant_keys = [10, 0, 16, 17, 28]
        for key in non_existant_keys:
            with self.assertRaises(KeyError, msg="Remove should raise a key error if the node is not present in the tree,"):
                tree.remove(key)


    def test_length_on_empty_tree(self):
        tree = RedBlackTree()
        self.assertEqual(len(tree), 0, "An empty tree should have a length of 0.")


    def test_length_on_duplicates(self):
        tree = RedBlackTree()
        # There are 7 unique keys (1, 2, 3, 4, 5, 6, 7)
        keys = [5, 3, 2, 1, 4, 1, 2, 6, 7, 1, 5, 4, 3, 2, 1]
        for key in keys:
            tree.add(key)
        self.assertEqual(len(tree), 7, "Duplicates should not be counted in the tree length.")


class TestVanillaBST(unittest.TestCase):

    def test_add_and_remove(self):

        tree = VanillaBST()

        keys = [1, 2, 3, 4, 5, 20, 15, 14, 13, 12, 11, 6, 7, 8, 9, 19, 18, 25, 23, 24, 22, 21, 64, 66, 67, 69, 37, 39, 70, 73, 40, 75, 42, 76, 46, 47, 49, 53, 58, 62]
        for key in keys:
            tree.add(key)
            self.assertTrue(key in tree, "Key {} should be in the tree".format(key))

        for key in keys:
            tree.remove(key)
            self.assertFalse(key in tree, "Key {} should no longer be in the tree.".format(key))


    def test_remove_on_not_present(self):
        tree = VanillaBST()

        keys = [1, 2, 3, 4, 5, 20, 15, 14, 13, 12, 11, 6, 7, 8, 9, 19, 18, 25, 23, 24, 22, 21, 64, 66, 67, 69, 37, 39, 70, 73, 40, 75, 42, 76, 46, 47, 49, 53, 58, 62]
        for key in keys: tree.add(key)
        non_existant_keys = [10, 0, 16, 17, 28]
        for key in non_existant_keys:
            with self.assertRaises(KeyError, msg="Remove should raise a key error if the node is not present in the tree,"):
                tree.remove(key)


    def test_length_on_empty_tree(self):
        tree = VanillaBST()
        self.assertEqual(len(tree), 0, "An empty tree should have a length of 0.")


    def test_length_on_duplicates(self):
        tree = VanillaBST()
        # There are 7 unique keys (1, 2, 3, 4, 5, 6, 7)
        keys = [5, 3, 2, 1, 4, 1, 2, 6, 7, 1, 5, 4, 3, 2, 1]
        for key in keys:
            tree.add(key)
        self.assertEqual(len(tree), 7, "Duplicates should not be counted in the tree length.")



if __name__ == '__main__':
    unittest.main()
