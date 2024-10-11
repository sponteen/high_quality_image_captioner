import sys
from typing import List, Tuple, Callable, Any


def get_top_item(
    items: List[Any],
    callable: Callable,
    *args,
    **kwargs,
) -> Tuple[float, Any]:
    top_score = float("-inf")
    top_result = None

    for item in items:
        result = callable(item, *args, **kwargs)
        if (
            isinstance(
                result,
                (
                    tuple,
                    list,
                ),
            )
            and len(result) == 2
        ):
            (
                score,
                result,
            ) = result
        else:
            (
                score,
                result,
            ) = (
                result,
                item,
            )

        if top_score < score:
            top_score = score
            top_result = result

    return (
        top_score,
        top_result,
    )
