# tree-lib

Tree-lib provides 2 classes: AbstractBST and RedBlackTree. AbstractBST is an abstract base class providing helper methods for binary search tree implementations, and RedBlackTree is an implementation of a balanced binary search tree.

## AbstractBST

To implement AbstractBST, the implementing class will need to provide concrete implementations for the ```_add``` and ```_remove``` abstract methods. The root node will need to be attached to ```self.root```, and the add and remove functions will need to maintain the binary search tree property (https://en.wikipedia.org/wiki/Binary_search_tree#Definition) so that the contains and in-order traversal methods provided by AbstractBST work correctly. 

### Helper methods for subclasses

In addition to implementing the [MutableSet abc](https://docs.python.org/3.6/library/collections.abc.html#collections.abc.MutableSet), AbstractBST provides 4 search methods, 4 tree editing methods, and 2 balancing methods to assist sub classes in implementing the abstract methods.

#### `find_node(self, key: int) -> "TreeNode"`

Finds and returns the node with the given key. If no node with the key is found, None is returned.

#### `find_new_parent_node(self, key) -> "TreeNode"`

Returns the potential parent node for the given key. This is defined using the standard BST add definition -- we will want to add the new key as a leaf node, and so need to find the first suitable parent node with an empty left or right slot. Raises a KeyError if the the given key is already in the BST.

#### `in_order_successor(self, node: "TreeNode") -> "TreeNode"`

Locates and returns the inorder successor of the given node. If the given node is the last node in the tree (and thus has no in-order successor), None is returned. Raises a TypeError if node is not a TreeNode.

#### `node_within_subtree(self, lower_node: "TreeNode", upper_node: "TreeNode") -> bool`

Checks whether or not lower_node is within the subtree of upper_node. This is True if lower_node is within the upper_node subtree, False if not. True is also returned in the case that lower_node and upper_node are referring to the same node.

If upper_node is None, False is returned. If lower_node is None, True is returned. This is because the subtree rooted at upper_node cannot contain any nodes, let alone lower_node, if it is None. On the other hand, all leaf node have implicit None children.

This method is useful for protecting against unintended branch severing and cycles caused by moving a subtree lower within itself.

#### `replace_node(self, old_node: "TreeNode", new_node: "TreeNode") -> None`

Substitutes new_node into the tree in place of old_node. old_node is completely removed from the tree, with new_node taking its place. old_node's parent left subtree, and right subtree all become new_node's. If new_node had children in its old location, the parent of these will be set to None and they will be detached from the tree. It is the responsibility of the caller to manage these now "loose" branches. Raises a TypeError if old_node or new_node is None.

#### `replace_subtree(self, old_subtree: "TreeNode", new_subtree: "TreeNode") -> None`

Replaces old_subtree with new_subtree. old_subtree's parent will instead link to new_subtree and if old_subtree was the tree root, new_subtree will become the tree root. If new_subtree is already elsewhere in the BST, it will be removed from the old location. old_subtree's parent link will also be severed. Raises a TypeError if old_subtree is None or a ValueError if old_subtree is within new_subtree.

#### `replace_right_subtree(self, parent: "TreeNode", new_subtree: "TreeNode") -> None`

Replaces the right subtree of parent with new_subtree. The old parent.right is completely removed from the tree -- it is up to the caller to hold a reference to this branch if it will then need to be transplanted elsewhere. Raises a TypeError if parent is None.

#### `replace_left_subtree(self, parent: "TreeNode", new_subtree: "TreeNode") -> None`

Replaces the left subtree of parent with new_subtree. The old parent.left is completely removed from the tree -- it is up to the caller to hold a reference to this branch if it will then need to be transplanted elsewhere. Raises a TypeError if parent is None.

#### `rotate_left(self, node_to_rotate: "TreeNode") -> None`

Takes a node that has a right child, and modifies the tree such that the node is now the left child of its original right child, and
then moves other branches so that the tree remains valid. This method is intended for use by self-balancing implementations. Raises a TypeError if node_to_rotate is None or a ValueError if node_to_rotate has no right child.

#### `rotate_right(self, node_to_rotate: "TreeNode") -> None`

Takes a node that has a left child, and modifies the tree such that the node is now the right child of its original left child, and
then moves other branches so that the tree remains valid. This method is intended for use by self-balancing implementations. Raises a TypeError if node_to_rotate is None or a ValueError if node_to_rotate has no left child.

### Example

Here is an example of using AbstractBST to implement a BST using the bread and butter textbook add and remove strategies.

```py
from abstract_tree import AbstractBST

class BST(AbstractBST):

     def _add(self, key):

        # If the tree is empty, new node should be the root node.
        if not self:
            self.root = BST.TreeNode(key, None)
            return self.root

        # Find a suitable parent node to attach the new node to.
        # find_new_parent_node raises an error if the key is already
        # in the tree.
        try:
            parent_node = self.find_new_parent_node(key)
        except:
            # We need to return None so that AbstractBST knows no node was added.
            return None

        # Create a new node and check which side of parent_node to
        # attach it to.
        new_node = BST.TreeNode(key, parent_node)
        if parent_node.key < new_node.key:
            parent_node.right = new_node
        else:
            parent_node.left = new_node

        # Return the new node.
        return new_node
        
   def _discard(self, key):
   # Find the target node in the tree. If the node does not exist,
   # AbstractBST will throw a KeyError, as per the MutableSet.discard
   # specifications. This is taken care of for you, so your code can
   # just assume find_node will return a valid node.
   target_node = self.find_node(key)

   # There is, at most, a right child. Use AbstractBST.replace_subtree to
   # replace the node we want to delete with its right subtree.
   if target_node.left is None:
       self.replace_subtree(target_node, target_node.right)
       return

   # There is only a left child.
   if target_node.right is None:
       self.replace_subtree(target_node, target_node.left)
       return

   # There are 2 children. Use the text book strategy of finding the
   # inorder successor (using AbstractBST.in_order_successor) so that we
   # can replace it with it, and then use AbstractBST.replace_subtree,
   # to replace the inorder successor with its right child, and 
   # AbstractBST.replace_node to replace the target node with the 
   # successor.
   successor = self.in_order_successor(target_node)
   self.replace_subtree(successor, successor.right)
   self.replace_node(target_node, successor)
```

### Using AbstractBST implementations

AbstractBST implements the MutableSet abstract base class, and so usage of implementations of AbstractBST is the same as the built in python `set`. There are pros and cons to using a Tree implementation of a set, as opposed to the built in hash set. The main advantage is that the **keys are maintained in a sorted order**, allowing them to be returned in sorted order in O(n) time. On the downside, the standard operations of add, contains, and remove are O(log(n)), as opposed to the O(1) achieved by a hash set. An unbalanced tree implementation (like the BST example above) could even take O(n) time on these basic operations. Balanced trees, such as Red-Black Trees ensure the operations are always O(log(n)).

Using the BST class we defined above, here is an example of the usage.

```
tree = BST()

keys = [10, 8, 9, 4, 5, 2, 1, 7, 3, 6]

# Add the keys
for key in keys:
    tree.add(key)
    # Ensure the key is now in the tree.
    assert(key in tree)

# Use the iterator to return the keys in order
# Will print: [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
print(list(tree))

# Check the length of the tree.
# Will print: 10
print(len(tree))

# Remove the keys
for key in keys:
    assert(key in tree)
    tree.remove(key)
    # Ensure the key has now been deleted.
    assert(key not in tree)
```



## RedBlackTree

