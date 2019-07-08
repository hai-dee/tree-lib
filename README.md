# tree-lib

Tree-lib provides 2 classes: AbstractBST and RedBlackTree. AbstractBST is an abstract base class providing helper methods for binary search tree implementations, and RedBlackTree is an implementation of a balanced binary search tree.

## AbstractBST

To implement AbstractBST, the implementing class will need to provide concrete implementations for the ```_add``` and ```_remove``` abstract methods. The root node will need to be attached to ```self.root```, and the add and remove functions will need to maintain the binary search tree property (https://en.wikipedia.org/wiki/Binary_search_tree#Definition) so that the contains and in-order traversal methods provided by AbstractBST work correctly. 

### Helper methods for subclasses

AbstractBST provides 4 search methods, 4 tree editing methods, and 2 balancing methods to assist sub classes in implementing the abstract methods.

#### find_node(self, key: int) -> "TreeNode"

#### find_new_parent_node(self, key) -> "TreeNode"

#### in_order_successor(self, node: "TreeNode") -> "TreeNode"

#### node_within_subtree(self, lower_node: "TreeNode", upper_node: "TreeNode") -> bool

#### replace_node(self, old_node: "TreeNode", new_node: "TreeNode") -> None

#### replace_subtree(self, old_subtree: "TreeNode", new_subtree: "TreeNode") -> None

#### replace_right_subtree(self, parent: "TreeNode", new_subtree: "TreeNode") -> None

#### replace_left_subtree(self, parent: "TreeNode", new_subtree: "TreeNode") -> None

#### rotate_left(self, node_to_rotate: "TreeNode") -> None

Takes a node that has a right child, and modifies the tree such
that the node is now the left child of its original right child, and
then moves other branches so that the tree remains valid.

This method is intended for use by self-balancing implementations.

Args:
  node_to_rotate: a node with a right child.

Raises:
  TypeError: node_to_rotate is None
  ValueError: node_to_rotate has no right child.

#### rotate_right(self, node_to_rotate: "TreeNode") -> None

Takes a node that has a left child, and modifies the tree such
that the node is now the right child of its original left child, and
then moves other branches so that the tree remains valid.

This method is intended for use by self-balancing implementations.

Args:
  node_to_rotate: a node with a left child.

Raises:
  TypeError: node_to_rotate is None.
  ValueError: node_to_rotate has no left child.

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


## RedBlackTree

