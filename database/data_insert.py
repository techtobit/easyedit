from sqlalchemy.ext.asyncio import AsyncSession
from database.processing_log import ProcessingLog

async def create_log(
    db: AsyncSession,
    user_id: int = 1,
    processing_time: float=None,
    status: str = "default",
    processed_img: str = None,
    ):
    log = ProcessingLog(
        user_id=user_id,
        processing_time=processing_time,
        status=status,
        processed_img=processed_img,
    )
    db.add(log)
    await db.commit()
    await db.refresh(log)
    return log
