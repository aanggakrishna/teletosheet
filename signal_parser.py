import re
from datetime import datetime
from logger import logger

def parse_new_signal(message_text, channel_id, channel_name, message_id):
    """Parse new signal message from Telegram channel"""
    try:
        data = {
            'timestamp_received': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'channel_id': channel_id,
            'channel_name': channel_name,
            'message_id': message_id,
            'current_status': 'active',
            'alert_history_last': 0,
            'update_history': ''
        }
        
        # Extract token name - skip SPONSORED and emoji lines
        lines = message_text.strip().split('\n')
        token_name_found = False
        raw_token_name = ''
        
        for line in lines:
            cleaned_line = re.sub(r'[^\w\s\-]', '', line).strip()
            # Skip empty lines, "SPONSORED", and lines with keywords
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
        chain_match = re.search(r'Chain:\s*(\w+)', message_text, re.IGNORECASE)
        data['chain'] = chain_match.group(1) if chain_match else ''
        
        # Extract price
        price_match = re.search(r'Price:\s*\$?([\d.]+)', message_text, re.IGNORECASE)
        data['price_entry'] = float(price_match.group(1)) if price_match else 0
        
        # Extract Market Cap
        mc_match = re.search(r'Market Cap:\s*\$?([\d.]+)([KMB]?)', message_text, re.IGNORECASE)
        if mc_match:
            mc_value = float(mc_match.group(1))
            mc_unit = mc_match.group(2).upper()
            multipliers = {'K': 1000, 'M': 1000000, 'B': 1000000000}
            data['mc_entry'] = mc_value * multipliers.get(mc_unit, 1)
        else:
            data['mc_entry'] = 0
        
        # Extract Liquidity
        liq_match = re.search(r'Liquidity:\s*\$?([\d.]+)([KMB]?)', message_text, re.IGNORECASE)
        if liq_match:
            liq_value = float(liq_match.group(1))
            liq_unit = liq_match.group(2).upper()
            multipliers = {'K': 1000, 'M': 1000000, 'B': 1000000000}
            data['liquidity'] = liq_value * multipliers.get(liq_unit, 1)
        else:
            data['liquidity'] = 0
        
        # Extract Volume 24h
        vol_match = re.search(r'Volume 24h:\s*\$?([\d.]+)([KMB]?)', message_text, re.IGNORECASE)
        if vol_match:
            vol_value = float(vol_match.group(1))
            vol_unit = vol_match.group(2).upper()
            multipliers = {'K': 1000, 'M': 1000000, 'B': 1000000000}
            data['volume_24h'] = vol_value * multipliers.get(vol_unit, 1)
        else:
            data['volume_24h'] = 0
        
        # Extract Bundles
        bundles_match = re.search(r'Bundles:\s*\d+\s*\((\d+)%\)', message_text, re.IGNORECASE)
        data['bundles_percent'] = int(bundles_match.group(1)) if bundles_match else 0
        
        # Extract Snipers
        snipers_match = re.search(r'Snipers:\s*\d+\s*\((\d+)%\)', message_text, re.IGNORECASE)
        data['snipers_percent'] = int(snipers_match.group(1)) if snipers_match else 0
        
        # Extract Dev %
        dev_match = re.search(r'Dev:\s*(\d+)%', message_text, re.IGNORECASE)
        data['dev_percent'] = int(dev_match.group(1)) if dev_match else 0
        
        # Extract Confidence
        conf_match = re.search(r'Confidence:\s*(\d+)%', message_text, re.IGNORECASE)
        data['confidence_score'] = int(conf_match.group(1)) if conf_match else 0
        
        # Extract Contract Address (CA) - Solana addresses are typically 32-44 characters
        ca_match = re.search(r'Contract:\s*([A-Za-z0-9]{32,44})', message_text, re.IGNORECASE)
        data['ca'] = ca_match.group(1) if ca_match else ''
        
        # Validate CA format (basic validation)
        if data['ca'] and len(data['ca']) < 32:
            logger.warning(f"Invalid CA length for {data['token_name']}: {data['ca']}")
            data['ca'] = ''  # Reset if invalid
        
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
        
        logger.debug(f"Parsed signal: {data['token_name']} | CA: {data['ca'][:8] if data['ca'] else 'None'}...")
        return data
        
    except Exception as e:
        logger.error(f"Error parsing signal from {channel_name}: {e}", exc_info=True)
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

