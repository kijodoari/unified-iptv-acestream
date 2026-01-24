"""
API endpoints for dashboard data
"""
import logging
import time
from datetime import datetime
from fastapi import APIRouter, Depends, Request, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.utils.auth import get_db
from app.models import Channel, User, Category, ScraperURL, EPGSource
from fastapi.responses import StreamingResponse
from fastapi.responses import StreamingResponse, Response
import aiohttp

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/dashboard/stats")
async def get_dashboard_stats(request: Request, db: Session = Depends(get_db)):
    """Get dashboard statistics"""
    
    # Get channel stats
    total_channels = db.query(Channel).count()
    online_channels = db.query(Channel).filter(Channel.is_online == True).count()
    active_channels = db.query(Channel).filter(Channel.is_active == True).count()
    
    # Get user stats
    total_users = db.query(User).count()
    active_users = db.query(User).filter(User.is_active == True).count()
    
    # Get category stats
    total_categories = db.query(Category).count()
    
    # Get scraper stats
    total_scraper_urls = db.query(ScraperURL).count()
    enabled_scraper_urls = db.query(ScraperURL).filter(ScraperURL.is_enabled == True).count()
    
    # Get EPG stats
    total_epg_sources = db.query(EPGSource).count()
    
    # Get active streams from aiohttp server
    active_streams = 0
    total_clients = 0
    try:
        aiohttp_server = request.app.state.aiohttp_streaming_server
        if aiohttp_server:
            # Get snapshot to avoid holding lock too long
            async with aiohttp_server.streams_lock:
                streams_snapshot = list(aiohttp_server.streams.values())
            
            active_streams = len(streams_snapshot)
            for stream in streams_snapshot:
                async with stream.lock:
                    total_clients += len(stream.clients)
    except Exception as e:
        logger.error(f"Error getting active streams: {e}")
    
    # Check AceStream engine health
    acestream_engine_status = {
        "status": "disabled",
        "available": False
    }
    try:
        aceproxy = request.app.state.aceproxy_service
        if aceproxy:
            acestream_engine_status = await aceproxy.check_engine_health()
    except Exception as e:
        logger.error(f"Error checking AceStream engine health: {e}")
        acestream_engine_status = {
            "status": "error",
            "available": False,
            "message": str(e)
        }
    
    return {
        "total_channels": total_channels,
        "online_channels": online_channels,
        "active_channels": active_channels,
        "total_users": total_users,
        "active_users": active_users,
        "total_categories": total_categories,
        "scraper_urls": total_scraper_urls,
        "enabled_scraper_urls": enabled_scraper_urls,
        "epg_sources": total_epg_sources,
        "active_streams": active_streams,
        "active_connections": total_clients,
        "acestream_engine": acestream_engine_status
    }


@router.get("/channels")
async def get_channels(
    limit: int = 100,
    offset: int = 0,
    db: Session = Depends(get_db)
):
    """Get channels list"""
    
    channels = db.query(Channel).filter(
        Channel.is_active == True
    ).order_by(
        Channel.display_order, Channel.name
    ).limit(limit).offset(offset).all()
    
    return [
        {
            "id": channel.id,
            "name": channel.name,
            "acestream_id": channel.acestream_id,
            "category": channel.category.name if channel.category else None,
            "logo_url": channel.logo_url,
            "is_online": channel.is_online,
            "is_active": channel.is_active,
            "created_at": channel.created_at.isoformat()
        }
        for channel in channels
    ]


@router.get("/channels/{channel_id}")
async def get_channel(
    channel_id: int,
    db: Session = Depends(get_db)
):
    """Get single channel details"""
    
    channel = db.query(Channel).filter(Channel.id == channel_id).first()
    if not channel:
        raise HTTPException(status_code=404, detail="Channel not found")
    
    return {
        "id": channel.id,
        "name": channel.name,
        "acestream_id": channel.acestream_id,
        "stream_url": channel.stream_url,
        "category": channel.category.name if channel.category else None,
        "category_id": channel.category_id,
        "logo_url": channel.logo_url,
        "epg_id": channel.epg_id,
        "language": channel.language,
        "country": channel.country,
        "description": channel.description,
        "is_online": channel.is_online,
        "is_active": channel.is_active,
        "created_at": channel.created_at.isoformat(),
        "updated_at": channel.updated_at.isoformat()
    }


@router.post("/channels")
async def create_channel(
    channel_data: dict,
    db: Session = Depends(get_db)
):
    """Create a new channel"""
    
    # Check if category exists or create it
    category = None
    if channel_data.get('category'):
        category = db.query(Category).filter(Category.name == channel_data['category']).first()
        if not category:
            category = Category(name=channel_data['category'])
            db.add(category)
            db.flush()
    
    # Create channel
    channel = Channel(
        name=channel_data['name'],
        acestream_id=channel_data.get('acestream_id'),
        stream_url=channel_data.get('stream_url'),
        category_id=category.id if category else None,
        logo_url=channel_data.get('logo_url'),
        epg_id=channel_data.get('epg_id'),
        language=channel_data.get('language'),
        country=channel_data.get('country'),
        description=channel_data.get('description'),
        is_active=True
    )
    
    db.add(channel)
    db.commit()
    db.refresh(channel)
    
    return {
        "id": channel.id,
        "name": channel.name,
        "message": "Channel created successfully"
    }


@router.put("/channels/{channel_id}")
async def update_channel(
    channel_id: int,
    channel_data: dict,
    db: Session = Depends(get_db)
):
    """Update a channel"""
    
    channel = db.query(Channel).filter(Channel.id == channel_id).first()
    if not channel:
        raise HTTPException(status_code=404, detail="Channel not found")
    
    # Update category if provided
    if 'category' in channel_data and channel_data['category']:
        category = db.query(Category).filter(Category.name == channel_data['category']).first()
        if not category:
            category = Category(name=channel_data['category'])
            db.add(category)
            db.flush()
        channel.category_id = category.id
    
    # Update other fields
    if 'name' in channel_data:
        channel.name = channel_data['name']
    if 'acestream_id' in channel_data:
        channel.acestream_id = channel_data['acestream_id']
    if 'stream_url' in channel_data:
        channel.stream_url = channel_data['stream_url']
    if 'logo_url' in channel_data:
        channel.logo_url = channel_data['logo_url']
    if 'epg_id' in channel_data:
        channel.epg_id = channel_data['epg_id']
    if 'is_active' in channel_data:
        channel.is_active = channel_data['is_active']
    if 'language' in channel_data:
        channel.language = channel_data['language']
    if 'country' in channel_data:
        channel.country = channel_data['country']
    if 'description' in channel_data:
        channel.description = channel_data['description']
    
    channel.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(channel)
    
    return {
        "id": channel.id,
        "name": channel.name,
        "message": "Channel updated successfully"
    }


@router.delete("/channels/{channel_id}")
async def delete_channel(
    channel_id: int,
    db: Session = Depends(get_db)
):
    """Delete a channel"""
    
    channel = db.query(Channel).filter(Channel.id == channel_id).first()
    if not channel:
        raise HTTPException(status_code=404, detail="Channel not found")
    
    db.delete(channel)
    db.commit()
    
    return {
        "message": "Channel deleted successfully"
    }


@router.post("/scraper/trigger")
async def trigger_scraping(db: Session = Depends(get_db)):
    """Trigger manual scraping"""
    from main import scraper_service
    
    logger.info("=== MANUAL SCRAPING TRIGGERED VIA API ===")
    
    if not scraper_service:
        logger.error("Scraper service not initialized")
        return {"status": "error", "message": "Scraper service not initialized"}
    
    try:
        # Pass db session to scraper
        start_time = time.time()
        logger.info("Starting scraping process...")
        results = await scraper_service.scrape_m3u_sources(db)
        elapsed = time.time() - start_time
        
        total_channels = sum(results.values())
        
        logger.info(f"=== SCRAPING COMPLETED: {total_channels} channels from {len(results)} source(s) in {elapsed:.2f}s ===")
        
        return {
            "status": "success",
            "message": f"Scraped {total_channels} channels from {len(results)} source(s)",
            "details": {
                "total_channels": total_channels,
                "sources_processed": len(results),
                "results": results,
                "elapsed_seconds": round(elapsed, 2)
            }
        }
    except Exception as e:
        logger.error(f"Error triggering scraping: {e}", exc_info=True)
        return {"status": "error", "message": str(e)}


@router.post("/epg/update")
async def update_epg(db: Session = Depends(get_db)):
    """Trigger EPG update"""
    # TODO: Implement EPG update trigger
    return {"status": "triggered", "message": "EPG update will start shortly"}


@router.post("/channels/check")
async def check_channels(db: Session = Depends(get_db)):
    """Check channel status"""
    # TODO: Implement channel status check
    return {"status": "triggered", "message": "Channel check will start shortly"}


@router.get("/hls/{channel_id}/manifest.m3u8")
async def proxy_hls_manifest(channel_id: int, request: Request, db: Session = Depends(get_db)):
    """Proxy HLS manifest from AceStream engine to browser"""
    channel = db.query(Channel).filter(Channel.id == channel_id).first()
    if not channel or not channel.acestream_id:
        raise HTTPException(status_code=404, detail="Channel not found or no AceStream ID")
    
    acestream_url = f"http://acestream:6878/ace/manifest.m3u8?id={channel.acestream_id}"
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(acestream_url, timeout=aiohttp.ClientTimeout(total=10)) as response:
                if response.status != 200:
                    raise HTTPException(status_code=response.status, detail="AceStream error")
                
                content = await response.text()
                
                # Rewrite ALL URLs in manifest to point to our proxy
                import re
                base_url = str(request.base_url).rstrip('/')
                
                # Replace absolute URLs
                content = re.sub(
                    r'http://acestream:6878/ace/',
                    f'{base_url}/api/hls/{channel_id}/',
                    content
                )
                
                # Replace relative URLs (lines that don't start with #)
                lines = content.split('\n')
                new_lines = []
                for line in lines:
                    if line and not line.startswith('#') and not line.startswith('http'):
                        # It's a relative path, prepend our proxy URL
                        new_lines.append(f'{base_url}/api/hls/{channel_id}/{line}')
                    else:
                        new_lines.append(line)
                
                content = '\n'.join(new_lines)
                
                return Response(content=content, media_type="application/vnd.apple.mpegurl")
    except aiohttp.ClientError as e:
        logger.error(f"Error proxying HLS manifest: {e}")
        raise HTTPException(status_code=503, detail=f"AceStream connection error: {str(e)}")


@router.get("/hls/{channel_id}/{segment:path}")
async def proxy_hls_segment(channel_id: int, segment: str, db: Session = Depends(get_db)):
    """Proxy HLS segments from AceStream engine to browser"""
    channel = db.query(Channel).filter(Channel.id == channel_id).first()
    if not channel or not channel.acestream_id:
        raise HTTPException(status_code=404, detail="Channel not found")
    
    # Construct AceStream URL
    acestream_url = f"http://acestream:6878/ace/{segment}"
    
    try:
        async def stream_proxy():
            async with aiohttp.ClientSession() as session:
                async with session.get(acestream_url, timeout=aiohttp.ClientTimeout(total=30)) as response:
                    if response.status != 200:
                        logger.error(f"AceStream segment error: {response.status} for {acestream_url}")
                        return
                    async for chunk in response.content.iter_chunked(8192):
                        yield chunk
        
        return StreamingResponse(stream_proxy(), media_type="video/MP2T")
    except Exception as e:
        logger.error(f"Error proxying HLS segment {segment}: {e}")
        raise HTTPException(status_code=503, detail=f"Segment streaming error: {str(e)}")
