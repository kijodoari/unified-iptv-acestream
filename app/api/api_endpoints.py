"""
API endpoints for dashboard data
"""
import asyncio
import logging
import time
import json
from datetime import datetime
from fastapi import APIRouter, Depends, Request, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.utils.auth import get_db
from app.models import Channel, User, Category, ScraperURL, EPGSource
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
async def trigger_scraping(background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    """Trigger manual scraping - returns immediately and runs in background"""
    from main import scraper_service
    
    logger.info("=== MANUAL SCRAPING TRIGGERED VIA API ===")
    
    if not scraper_service:
        logger.error("Scraper service not initialized")
        return {"status": "error", "message": "Scraper service not initialized"}
    
    # Retornar inmediatamente y ejecutar en background
    background_tasks.add_task(scraper_background, scraper_service, db)
    
    return {
        "status": "started",
        "message": "Scraping started in background. Use GET /api/scraper/stream for real-time progress.",
        "info": "The scraping is running in background and won't block the server. Check logs or use SSE endpoint for progress."
    }


async def scraper_background(scraper_service, db: Session):
    """Background task for scraping"""
    try:
        start_time = time.time()
        logger.info("Background scraping: Starting...")
        
        results = await scraper_service.scrape_m3u_sources(db)
        elapsed = time.time() - start_time
        
        total_channels = sum(results.values())
        
        logger.info(f"=== BACKGROUND SCRAPING COMPLETED: {total_channels} channels from {len(results)} source(s) in {elapsed:.2f}s ===")
        
    except Exception as e:
        logger.error(f"Error in background scraping: {e}", exc_info=True)


@router.post("/epg/update")
async def update_epg(request: Request, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    """Trigger EPG update - returns immediately and runs in background"""
    from main import epg_service
    
    logger.info("=== MANUAL EPG UPDATE TRIGGERED VIA API ===")
    
    if not epg_service:
        logger.error("EPG service not initialized")
        return {"status": "error", "message": "EPG service not initialized"}
    
    # Retornar inmediatamente y ejecutar en background
    background_tasks.add_task(epg_update_background, epg_service)
    
    return {
        "status": "started",
        "message": "EPG update started in background. Use GET /api/epg/stream for real-time progress.",
        "info": "The EPG update is running in background and won't block the server. Check logs or use SSE endpoint for progress."
    }


async def epg_update_background(epg_service):
    """Background task for EPG update"""
    try:
        start_time = time.time()
        logger.info("Background EPG update: Starting...")
        
        programs_count = await epg_service.update_all_epg()
        elapsed = time.time() - start_time
        
        logger.info(f"=== BACKGROUND EPG UPDATE COMPLETED: {programs_count} programs in {elapsed:.2f}s ===")
        
    except Exception as e:
        logger.error(f"Error in background EPG update: {e}", exc_info=True)


@router.post("/channels/check")
async def check_channels(request: Request, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    """Check channel status - returns immediately and runs in background"""
    from main import aceproxy_service
    
    logger.info("=== MANUAL CHANNEL CHECK TRIGGERED VIA API ===")
    
    if not aceproxy_service:
        logger.error("AceProxy service not initialized")
        return {"status": "error", "message": "AceProxy service not initialized"}
    
    # Retornar inmediatamente y ejecutar en background
    background_tasks.add_task(check_channels_background, aceproxy_service, db)
    
    return {
        "status": "started",
        "message": "Channel check started in background. Use GET /api/channels/check/stream for real-time progress.",
        "info": "The check is running in background and won't block the server. Check logs or use SSE endpoint for progress."
    }


async def check_channels_background(aceproxy_service, db: Session):
    """Background task for checking channels - PARALLEL execution"""
    try:
        start_time = time.time()
        channels = db.query(Channel).filter(Channel.is_active == True).all()
        
        if not channels:
            logger.info("No channels to check")
            return
        
        total_channels = len(channels)
        checked = 0
        online = 0
        offline = 0
        skipped = 0
        
        logger.info(f"Background check: Found {total_channels} channels")
        
        # Separate channels with and without acestream_id
        channels_to_check = [ch for ch in channels if ch.acestream_id]
        skipped = total_channels - len(channels_to_check)
        
        if skipped > 0:
            logger.info(f"Skipping {skipped} channels without AceStream ID")
        
        # Check channels in parallel (batches of 5 to avoid overwhelming AceStream engine)
        batch_size = 5
        
        async def check_single_channel(channel, index):
            """Check a single channel"""
            try:
                logger.info(f"[{index}/{len(channels_to_check)}] Checking {channel.name}")
                is_available = await aceproxy_service.check_stream_availability(channel.acestream_id)
                channel.is_online = is_available
                channel.last_checked = datetime.utcnow()
                channel.updated_at = datetime.utcnow()
                
                status = "ONLINE" if is_available else "OFFLINE"
                logger.info(f"[{index}/{len(channels_to_check)}] {status}: {channel.name}")
                
                return is_available
            except Exception as e:
                logger.warning(f"[{index}/{len(channels_to_check)}] Error checking {channel.name}: {e}")
                channel.is_online = False
                channel.last_checked = datetime.utcnow()
                channel.updated_at = datetime.utcnow()
                return False
        
        # Process in batches
        for i in range(0, len(channels_to_check), batch_size):
            batch = channels_to_check[i:i + batch_size]
            batch_start = i + 1
            
            logger.info(f"Processing batch {i//batch_size + 1}/{(len(channels_to_check) + batch_size - 1)//batch_size} ({len(batch)} channels)")
            
            # Check all channels in batch in parallel
            tasks = [check_single_channel(ch, batch_start + idx) for idx, ch in enumerate(batch)]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Count results
            for result in results:
                if isinstance(result, Exception):
                    offline += 1
                elif result:
                    online += 1
                else:
                    offline += 1
                checked += 1
            
            # Commit after each batch
            db.commit()
            logger.info(f"Batch complete: {checked}/{len(channels_to_check)} checked ({online} online, {offline} offline)")
        
        elapsed = time.time() - start_time
        
        logger.info(f"=== BACKGROUND CHECK COMPLETED: {checked} checked, {online} online, {offline} offline, {skipped} skipped in {elapsed:.2f}s ===")
        
    except Exception as e:
        logger.error(f"Error in background check: {e}", exc_info=True)


@router.get("/channels/check/stream")
async def check_channels_stream(request: Request, db: Session = Depends(get_db)):
    """Check channel status with real-time progress via Server-Sent Events - PARALLEL"""
    from main import aceproxy_service
    
    async def event_generator():
        try:
            yield f"data: {json.dumps({'type': 'start', 'message': 'Starting parallel channel check...'})}\n\n"
            
            if not aceproxy_service:
                yield f"data: {json.dumps({'type': 'error', 'message': 'AceProxy service not initialized'})}\n\n"
                return
            
            start_time = time.time()
            channels = db.query(Channel).filter(Channel.is_active == True).all()
            
            if not channels:
                yield f"data: {json.dumps({'type': 'complete', 'message': 'No channels to check', 'details': {'total': 0}})}\n\n"
                return
            
            total_channels = len(channels)
            
            # Separate channels with and without acestream_id
            channels_to_check = [ch for ch in channels if ch.acestream_id]
            skipped = total_channels - len(channels_to_check)
            
            if skipped > 0:
                yield f"data: {json.dumps({'type': 'info', 'message': f'Found {len(channels_to_check)} channels to check ({skipped} skipped without AceStream ID)'})}\n\n"
            else:
                yield f"data: {json.dumps({'type': 'info', 'message': f'Found {len(channels_to_check)} channels to check'})}\n\n"
            
            checked = 0
            online = 0
            offline = 0
            
            # Check channels in parallel (batches of 5 to avoid overwhelming AceStream engine)
            batch_size = 5
            
            async def check_single_channel(channel, index):
                """Check a single channel and return result"""
                try:
                    check_start = time.time()
                    is_available = await aceproxy_service.check_stream_availability(channel.acestream_id)
                    check_elapsed = time.time() - check_start
                    
                    channel.is_online = is_available
                    channel.last_checked = datetime.utcnow()
                    channel.updated_at = datetime.utcnow()
                    
                    status = "online" if is_available else "offline"
                    
                    return {
                        'success': True,
                        'channel': channel,
                        'status': status,
                        'check_time': round(check_elapsed, 2),
                        'index': index
                    }
                except Exception as e:
                    channel.is_online = False
                    channel.last_checked = datetime.utcnow()
                    channel.updated_at = datetime.utcnow()
                    
                    return {
                        'success': False,
                        'channel': channel,
                        'status': 'error',
                        'error': str(e),
                        'index': index
                    }
            
            # Process in batches
            for batch_num, i in enumerate(range(0, len(channels_to_check), batch_size), 1):
                batch = channels_to_check[i:i + batch_size]
                batch_start = i + 1
                
                yield f"data: {json.dumps({'type': 'batch_start', 'batch': batch_num, 'size': len(batch), 'message': f'Checking batch {batch_num} ({len(batch)} channels in parallel)...'})}\n\n"
                
                # Check all channels in batch in parallel
                tasks = [check_single_channel(ch, batch_start + idx) for idx, ch in enumerate(batch)]
                results = await asyncio.gather(*tasks)
                
                # Process results and send updates
                for result in results:
                    channel = result['channel']
                    
                    if result['success']:
                        if result['status'] == 'online':
                            online += 1
                        else:
                            offline += 1
                        
                        yield f"data: {json.dumps({'type': 'progress', 'index': result['index'], 'total': len(channels_to_check), 'channel': {'id': channel.id, 'name': channel.name, 'status': result['status'], 'check_time': result['check_time']}, 'stats': {'checked': checked + 1, 'online': online, 'offline': offline, 'skipped': skipped}})}\n\n"
                    else:
                        offline += 1
                        yield f"data: {json.dumps({'type': 'progress', 'index': result['index'], 'total': len(channels_to_check), 'channel': {'id': channel.id, 'name': channel.name, 'status': 'error', 'error': result['error']}, 'stats': {'checked': checked + 1, 'online': online, 'offline': offline, 'skipped': skipped}})}\n\n"
                    
                    checked += 1
                
                # Commit after each batch
                db.commit()
                
                yield f"data: {json.dumps({'type': 'batch_complete', 'batch': batch_num, 'message': f'Batch {batch_num} complete', 'stats': {'checked': checked, 'online': online, 'offline': offline}})}\n\n"
            
            elapsed = time.time() - start_time
            
            yield f"data: {json.dumps({'type': 'complete', 'message': f'Check completed: {checked} checked, {online} online, {offline} offline, {skipped} skipped in {round(elapsed, 2)}s', 'details': {'total_channels': total_channels, 'checked': checked, 'online': online, 'offline': offline, 'skipped': skipped, 'elapsed_seconds': round(elapsed, 2)}})}\n\n"
            
        except Exception as e:
            yield f"data: {json.dumps({'type': 'error', 'message': str(e)})}\n\n"
    
    return StreamingResponse(event_generator(), media_type="text/event-stream")


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
