import ast
from unittest import (
    TestCase,
)
from darglint.analysis.return_visitor import (
    ReturnVisitor,
)
from darglint.analysis.function_scoped_visitor import (
    FunctionScopedVisitorMixin,
)
from .utils import (
    reindent,
)


class ScopedReturnVisitor(FunctionScopedVisitorMixin, ReturnVisitor):
    pass


class FunctionScopedVisitorMixinTests(TestCase):

    def assertFound(self, program):
        """Assert that the return was found.

        Args:
            program: The program to run the analysis on.

        Returns:
            The visitor, in case you want to do more analysis.

        """
        function = ast.parse(reindent(program)).body[0]
        visitor = ScopedReturnVisitor()
        visitor.visit(function)
        self.assertTrue(visitor.returns)
        return visitor

    def assertNoneFound(self, program):
        """Assert that no return was found.

        Args:
            program: The program to run the analysis on.

        Returns:
            The visitor, in case you want to do more analysis.

        """
        function = ast.parse(reindent(program)).body[0]
        visitor = ScopedReturnVisitor()
        visitor.visit(function)
        self.assertEqual(visitor.returns, [])
        return visitor

    def test_nested_return(self):
        program = r'''
            def f():
                def g():
                    return 'Hello nesting!'
                print(g())
        '''
        self.assertNoneFound(program)

    def test_deeply_nested_return(self):
        program = r'''
            def f():
                def g():
                    def h():
                        def i():
                            return 'Hello deeply nesting!'
                        print(i())
                    h()
                g()
        '''
        self.assertNoneFound(program)

    def test_only_outermost_captured(self):
        """Test that only the outermost function is analyzed.

        Rather than capturing all nested ones here, we'll extract the
        functions separately, and run analysis on them independently of
        one another.

        That should simplify the whole process by making it a bit more
        recursive.  Also, it will allow us to ignore nesting if we want.

        """
        program = r'''
            def f():
                def g():
                    return 3
                yield g()
        '''
        self.assertNoneFound(program)

    def test_outer_async_function_captured(self):
        program = r'''
            async def f():
                return 3
        '''
        self.assertFound(program)

    def test_inner_async_skipped(self):
        program = r'''
            async def f():
                async def g():
                    return 3
                yield await g()
        '''
        self.assertNoneFound(program)