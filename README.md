# tree-lib

Tree-lib provides 2 classes: AbstractBST and RedBlackTree. AbstractBST is an abstract base class providing helper methods for binary search tree implementations, and RedBlackTree is an implementation of a balanced binary search tree.

## AbstractBST

To implement AbstractBST, the implementing class will need to provide concrete implementations for the ```_add``` and ```_remove``` functions. The root node will need to be attached to ```self.root```, and the add and remove functions will need to maintain the binary search tree property (https://en.wikipedia.org/wiki/Binary_search_tree#Definition) so that the contains and in-order traversal methods provided by AbstractBST work correctly. 

### Example

Here is an example of using AbstractBST to implement a BST using the basic textbook add and remove functions.

```
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
```


## RedBlackTree

