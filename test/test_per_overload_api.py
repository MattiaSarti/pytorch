# Owner(s): ["module: unknown"]
import torch
import copy
from torch.testing._internal.common_utils import TestCase, run_tests

class TestPerOverloadAPI(TestCase):
    def test_basics_opoverloadpacket(self):
        # add is ony used as an example here. It is ok to update the test
        # if the semantics of add are modified in the future.
        add_packet = torch.ops.aten.add

        # class attributes
        self.assertEqual(add_packet.__name__, 'add')
        self.assertEqual(str(add_packet), 'aten.add')

        # callable
        self.assertEqual(add_packet(torch.tensor(2), torch.tensor(3)), torch.tensor(5))

        # correct module
        self.assertEqual(add_packet.__module__, add_packet.op.__module__)

        # caching
        another_add_packet = torch.ops.aten.add
        self.assertEqual(id(add_packet), id(another_add_packet))

        # deepcopy is a no-op
        self.assertEqual(id(add_packet), id(copy.deepcopy(add_packet)))

        # pretty print
        self.assertEqual(repr(add_packet), "<OpOverloadPacket(op='aten.add')>")

        self.assertRaises(AttributeError, lambda: add_packet.foo)

    def test_basics_opoverload(self):
        # add is ony used as an example here. It is ok to update the test
        # if the semantics of add are modified in the future.
        add_packet = torch.ops.aten.add
        add_tensoroverload = add_packet.Tensor

        # class attributes
        self.assertEqual(str(add_tensoroverload), 'aten.add.Tensor')
        self.assertEqual(add_tensoroverload.__name__, 'add.Tensor')
        self.assertEqual(add_tensoroverload.overloadpacket, add_packet)

        # deepcopy is a no-op
        self.assertEqual(id(add_tensoroverload), id(copy.deepcopy(add_tensoroverload)))

        # caching
        another_add_tensoroverload = torch.ops.aten.add.Tensor
        self.assertEqual(id(add_tensoroverload), id(another_add_tensoroverload))

        # pretty print
        self.assertEqual(repr(add_tensoroverload), "<OpOverload(op='aten.add', overload='Tensor')>")

        # callable
        self.assertEqual(add_tensoroverload(torch.tensor(2), torch.tensor(3)), torch.tensor(5))

        a = torch.tensor(2)
        b = torch.tensor(0)
        torch.ops.aten.add.out(a, a, out=b)
        self.assertEqual(b, torch.tensor(4))

        self.assertRaises(RuntimeError, lambda: add_tensoroverload(a, a, out=b))

        add_outoverload = add_packet.out
        self.assertEqual(str(add_outoverload.inputs), "(Tensor self, Tensor other, Scalar alpha, Tensor& out)")
        self.assertTrue(add_outoverload.inputs[3].is_mutable)
        self.assertTrue(not add_outoverload.inputs[2].is_mutable)
        self.assertTrue(add_outoverload.inputs[3].kwarg_only)
        self.assertTrue(add_outoverload.inputs[2].has_default_value)
        self.assertEqual(add_outoverload.inputs[2].default_value, 1)
        self.assertEqual(add_outoverload.inputs[2].name, "alpha")
        self.assertEqual(add_outoverload.inputs[2].type, torch.NumberType.get())
        self.assertEqual(add_outoverload.inputs[0].type, torch.TensorType.get())

if __name__ == '__main__':
    run_tests()
