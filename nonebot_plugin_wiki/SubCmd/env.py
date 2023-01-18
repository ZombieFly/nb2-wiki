from admin import add, rm, set


async def ADD(args: dict) -> str:
    args['group_id'] = 0
    return await add(args)


async def RM(args: dict) -> str:
    args['group_id'] = 0
    return await rm(args)


async def SET(args: dict) -> str:
    args['group_id'] = 0
    return await set(args)
