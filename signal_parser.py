import re
from datetime import datetime
from logger import logger
from channel_formats import get_format_for_channel

def parse_new_signal(message_text, channel_id, channel_name, message_id):
    """Parse new signal message from Telegram channel - supports multiple formats"""
    try:
        # Get the appropriate format for this channel
        format_config = get_format_for_channel(channel_id)
        logger.debug(f"Using format '{format_config['name']}' for channel {channel_name}")
        
        data = {
            'timestamp_received': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'channel_id': channel_id,
            'channel_name': channel_name,
            'message_id': message_id,
            'current_status': 'active',
            'alert_history_last': 0,
            'update_history': ''
        }
        
        # Use format-specific patterns
        patterns = format_config['patterns']
        
        # Extract token name using format-specific pattern
        token_match = re.search(patterns.get('token_name', r'([A-Z][A-Za-z0-9\s\-]+)'), message_text, re.MULTILINE)
        if token_match:
            data['token_name'] = re.sub(r'[^\w\s\-]', '', token_match.group(1)).strip()
        else:
            # Fallback to line-by-line extraction
            lines = message_text.strip().split('\n')
            token_name_found = False
            raw_token_name = ''
            
            for line in lines:
                cleaned_line = re.sub(r'[^\w\s\-]', '', line).strip()
                if cleaned_line and cleaned_line.upper() != 'SPONSORED' and not any(
                    keyword in line.upper() for keyword in ['CONTRACT', 'CHAIN', 'PRICE', 'MARKET', 'LIQUIDITY', 'VOLUME', 'BUNDLES', 'SNIPERS', 'DEX', 'CONFIDENCE']
                ):
                    raw_token_name = cleaned_line
                    token_name_found = True
                    break
            
            data['token_name'] = raw_token_name if token_name_found else 'Unknown'
        
        # If sponsored message, mark it
        if 'SPONSORED' in message_text.upper()[:50]:
            logger.debug(f"Sponsored signal detected: {data['token_name']}")
        
        # Extract chain
        if 'chain' in patterns:
            chain_match = re.search(patterns['chain'], message_text, re.IGNORECASE | re.MULTILINE)
            data['chain'] = chain_match.group(1) if chain_match else ''
        else:
            data['chain'] = ''
        
        # Extract price
        if 'price' in patterns:
            price_match = re.search(patterns['price'], message_text, re.IGNORECASE)
            data['price_entry'] = float(price_match.group(1)) if price_match else 0
        else:
            data['price_entry'] = 0
        
        # Extract Market Cap with K/M/B multipliers
        if 'market_cap' in patterns:
            mc_match = re.search(patterns['market_cap'], message_text, re.IGNORECASE)
            if mc_match:
                mc_value = float(mc_match.group(1))
                mc_unit = mc_match.group(2).upper() if len(mc_match.groups()) > 1 else ''
                multipliers = {'K': 1000, 'M': 1000000, 'B': 1000000000}
                data['mc_entry'] = mc_value * multipliers.get(mc_unit, 1)
            else:
                data['mc_entry'] = 0
        else:
            data['mc_entry'] = 0
        
        # Extract Liquidity
        if 'liquidity' in patterns:
            liq_match = re.search(patterns['liquidity'], message_text, re.IGNORECASE)
            if liq_match:
                liq_value = float(liq_match.group(1))
                liq_unit = liq_match.group(2).upper() if len(liq_match.groups()) > 1 else ''
                multipliers = {'K': 1000, 'M': 1000000, 'B': 1000000000}
                data['liquidity'] = liq_value * multipliers.get(liq_unit, 1)
            else:
                data['liquidity'] = 0
        else:
            data['liquidity'] = 0
        
        # Extract Volume 24h
        if 'volume_24h' in patterns:
            vol_match = re.search(patterns['volume_24h'], message_text, re.IGNORECASE)
            if vol_match:
                vol_value = float(vol_match.group(1))
                vol_unit = vol_match.group(2).upper() if len(vol_match.groups()) > 1 else ''
                multipliers = {'K': 1000, 'M': 1000000, 'B': 1000000000}
                data['volume_24h'] = vol_value * multipliers.get(vol_unit, 1)
            else:
                data['volume_24h'] = 0
        else:
            data['volume_24h'] = 0
        
        # Extract Bundles
        if 'bundles' in patterns:
            bundles_match = re.search(patterns['bundles'], message_text, re.IGNORECASE)
            data['bundles_percent'] = int(bundles_match.group(1)) if bundles_match else 0
        else:
            data['bundles_percent'] = 0
        
        # Extract Snipers
        if 'snipers' in patterns:
            snipers_match = re.search(patterns['snipers'], message_text, re.IGNORECASE)
            data['snipers_percent'] = int(snipers_match.group(1)) if snipers_match else 0
        else:
            data['snipers_percent'] = 0
        
        # Extract Dev %
        if 'dev' in patterns:
            dev_match = re.search(patterns['dev'], message_text, re.IGNORECASE)
            data['dev_percent'] = int(dev_match.group(1)) if dev_match else 0
        else:
            data['dev_percent'] = 0
        
        # Extract Confidence
        if 'confidence' in patterns:
            conf_match = re.search(patterns['confidence'], message_text, re.IGNORECASE)
            data['confidence_score'] = int(conf_match.group(1)) if conf_match else 0
        else:
            data['confidence_score'] = 0
        
        # Extract Contract Address (CA)
        if 'ca' in patterns:
            ca_match = re.search(patterns['ca'], message_text, re.IGNORECASE)
            data['ca'] = ca_match.group(1) if ca_match else ''
        else:
            data['ca'] = ''
        
        # Validate CA format (basic validation)
        if data['ca'] and len(data['ca']) < 32:
            logger.warning(f"Invalid CA length for {data['token_name']}: {data['ca']}")
            data['ca'] = ''  # Reset if invalid
        
        # Auto-fetch from API if format requires it
        auto_fetch = format_config.get('auto_fetch', False)
        if auto_fetch and data['ca']:
            logger.info(f"🔍 Auto-fetch mode for {format_config['name']} - fetching all data from API...")
            dex_data = fetch_dexscreener_data_sync(data['ca'])
            
            if dex_data:
                # ALWAYS use token name from API for auto-fetch formats (more reliable)
                api_token_name = dex_data.get('token_name', 'Unknown')
                if api_token_name and api_token_name != 'Unknown':
                    data['token_name'] = api_token_name
                
                # Override/fill all technical data from API
                data['chain'] = dex_data.get('chain', 'Solana')
                data['price_entry'] = dex_data.get('price', 0)
                data['mc_entry'] = dex_data.get('market_cap', 0)
                data['liquidity'] = dex_data.get('liquidity', 0)
                data['volume_24h'] = dex_data.get('volume_24h', 0)
                data['peak_mc'] = data['mc_entry']
                
                logger.success(f"✅ Auto-fetched: {data['token_name']} | Price=${data['price_entry']} | MC=${data['mc_entry']:,.0f}")
            else:
                logger.warning(f"⚠️ Could not auto-fetch data for CA: {data['ca'][:8]}...")
        
        # Generate links
        if data['ca']:
            data['link_dexscreener'] = f"https://dexscreener.com/solana/{data['ca']}"
            data['link_pump'] = f"https://pump.fun/{data['ca']}"
        else:
            data['link_dexscreener'] = ''
            data['link_pump'] = ''
        
        # Initialize tracking columns as empty
        for interval in [5, 10, 15, 30, 60]:
            data[f'price_{interval}min'] = ''
            data[f'mc_{interval}min'] = ''
            data[f'change_{interval}min'] = ''
        
        # Initialize alert columns
        data['peak_mc'] = data['mc_entry']
        data['peak_multiplier'] = 1.0
        data['alert_2x_time'] = ''
        data['alert_3x_time'] = ''
        data['alert_5x_time'] = ''
        data['alert_10x_time'] = ''
        data['error_log'] = ''
        
        # If SPONSORED message (missing price/mc data), fetch from DexScreener
        is_sponsored = 'SPONSORED' in message_text.upper()[:50]
        if is_sponsored and data['ca'] and (data['price_entry'] == 0 or data['mc_entry'] == 0):
            logger.info(f"📢 Sponsored signal detected for {data['token_name']}, fetching live data from DexScreener...")
            dex_data = fetch_dexscreener_data_sync(data['ca'])
            if dex_data:
                data['price_entry'] = dex_data.get('price', 0)
                data['mc_entry'] = dex_data.get('market_cap', 0)
                data['liquidity'] = dex_data.get('liquidity', 0)
                data['volume_24h'] = dex_data.get('volume_24h', 0)
                data['peak_mc'] = data['mc_entry']
                logger.success(f"✅ Fetched live data: Price=${data['price_entry']}, MC=${data['mc_entry']:,.0f}")
            else:
                logger.warning(f"⚠️ Could not fetch live data for {data['token_name']}")
        
        logger.debug(f"Parsed signal: {data['token_name']} | CA: {data['ca'][:8] if data['ca'] else 'None'}...")
        return data
        
    except Exception as e:
        logger.error(f"Error parsing signal from {channel_name}: {e}", exc_info=True)
        return None


def fetch_dexscreener_data_sync(ca):
    """Fetch price data from DexScreener synchronously (for signal parsing)"""
    try:
        import requests
        from config import DEXSCREENER_API_BASE
        
        if not ca or len(ca) < 32:
            return None
        
        url = f"{DEXSCREENER_API_BASE}/tokens/{ca}"
        response = requests.get(url, timeout=10)
        
        if response.status_code != 200:
            logger.debug(f"DexScreener API returned {response.status_code} for {ca[:8]}...")
            return None
        
        data = response.json()
        
        if not data.get('pairs'):
            logger.debug(f"No trading pairs found for {ca[:8]}...")
            return None
        
        # Get the first pair (usually the most liquid)
        pair = data['pairs'][0]
        
        # Extract token info
        base_token = pair.get('baseToken', {})
        chain_id = pair.get('chainId', 'solana')
        
        result = {
            'token_name': base_token.get('name', 'Unknown'),
            'token_symbol': base_token.get('symbol', ''),
            'chain': chain_id.capitalize(),
            'price': float(pair.get('priceUsd', 0)),
            'market_cap': float(pair.get('fdv', 0)),
            'liquidity': float(pair.get('liquidity', {}).get('usd', 0)),
            'volume_24h': float(pair.get('volume', {}).get('h24', 0))
        }
        
        return result
        
    except Exception as e:
        logger.debug(f"Error fetching DexScreener data: {e}")
        return None


def parse_alert_update(message_text):
    """Parse alert update message (e.g., '5x ALERT')"""
    try:
        data = {}
        
        # Extract multiplier
        mult_match = re.search(r'(\d+)x\s+ALERT', message_text, re.IGNORECASE)
        if not mult_match:
            return None
        
        data['multiplier'] = int(mult_match.group(1))
        
        # Extract token name
        token_match = re.search(r'🪙\s*(.+)', message_text)
        data['token_name'] = token_match.group(1).strip() if token_match else ''
        
        # Extract Time elapsed
        time_match = re.search(r'⏱️\s*Time:\s*(.+)', message_text, re.IGNORECASE)
        data['time_elapsed'] = time_match.group(1).strip() if time_match else ''
        
        # Extract CA (if present)
        ca_match = re.search(r'([A-Za-z0-9]{30,})', message_text)
        data['ca'] = ca_match.group(1) if ca_match else ''
        
        # Extract Entry MC
        entry_mc_match = re.search(r'Entry MC:\s*\$?([\d.]+)([KMB]?)', message_text, re.IGNORECASE)
        if entry_mc_match:
            mc_value = float(entry_mc_match.group(1))
            mc_unit = entry_mc_match.group(2).upper()
            multipliers = {'K': 1000, 'M': 1000000, 'B': 1000000000}
            data['entry_mc'] = mc_value * multipliers.get(mc_unit, 1)
        
        # Extract Current MC
        current_mc_match = re.search(r'Current MC:\s*\$?([\d.]+)([KMB]?)', message_text, re.IGNORECASE)
        if current_mc_match:
            mc_value = float(current_mc_match.group(1))
            mc_unit = current_mc_match.group(2).upper()
            multipliers = {'K': 1000, 'M': 1000000, 'B': 1000000000}
            data['current_mc'] = mc_value * multipliers.get(mc_unit, 1)
        
        # Extract Gain
        gain_match = re.search(r'Gain:\s*([\d.]+)x', message_text, re.IGNORECASE)
        data['gain'] = float(gain_match.group(1)) if gain_match else data['multiplier']
        
        # Extract Peak
        peak_match = re.search(r'Peak:\s*([\d.]+)x', message_text, re.IGNORECASE)
        data['peak'] = float(peak_match.group(1)) if peak_match else data['multiplier']
        
        data['alert_time'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        logger.debug(f"Parsed alert: {data['multiplier']}x for {data.get('token_name', 'Unknown')} (Time: {data.get('time_elapsed', 'N/A')})")
        return data
        
    except Exception as e:
        logger.error(f"Error parsing alert update: {e}", exc_info=True)
        return None


def is_signal_message(message_text):
    """Check if message is a new signal"""
    keywords = ['Contract:', 'Market Cap:', 'Chain:', 'Confidence:']
    is_signal = any(keyword in message_text for keyword in keywords)
    if is_signal:
        logger.debug("Message identified as signal")
    return is_signal


def is_alert_message(message_text):
    """Check if message is an alert update"""
    is_alert = re.search(r'\d+x\s+ALERT', message_text, re.IGNORECASE) is not None
    if is_alert:
        logger.debug("Message identified as alert")
    return is_alert

