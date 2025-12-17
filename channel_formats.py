"""
Multi-format signal parser configurations
Supports different channel formats
"""

# Channel format definitions
CHANNEL_FORMATS = {
    # Format 1: Standard format with labeled fields
    'standard': {
        'name': 'Standard Format',
        'example': '''
🚀 TOKEN NAME
Chain: Solana
Price: $0.00001
Market Cap: $100K
Liquidity: $50K
Volume 24h: $25K
Bundles: 5 (10%)
Snipers: 3 (5%)
Dev: 0%
Confidence: 85%
Contract: ABC123...XYZ789
        ''',
        'patterns': {
            'token_name': r'^[🚀💎⚡🔥]*\s*([A-Z][A-Za-z0-9\s\-]+)',
            'chain': r'Chain:\s*(\w+)',
            'price': r'Price:\s*\$?([\d.]+)',
            'market_cap': r'Market Cap:\s*\$?([\d.]+)([KMB]?)',
            'liquidity': r'Liquidity:\s*\$?([\d.]+)([KMB]?)',
            'volume_24h': r'Volume 24h:\s*\$?([\d.]+)([KMB]?)',
            'bundles': r'Bundles:\s*\d+\s*\((\d+)%\)',
            'snipers': r'Snipers:\s*\d+\s*\((\d+)%\)',
            'dev': r'Dev:\s*(\d+)%',
            'confidence': r'Confidence:\s*(\d+)%',
            'ca': r'(?:Contract|CA):\s*([A-Za-z0-9]{32,44})'
        }
    },
    
    # Format 2: Compact format with symbols
    'compact': {
        'name': 'Compact Format',
        'example': '''
💎 TOKEN NAME | SOL
💵 $0.00001 | MC: $100K | LIQ: $50K
📊 Vol: $25K | B: 10% | S: 5%
🔒 Dev: 0% | Score: 85%
📝 ABC123...XYZ789
        ''',
        'patterns': {
            'token_name': r'^[💎🚀⚡🔥]+\s*([A-Z][A-Za-z0-9\s\-]+)\s*\|',
            'chain': r'\|\s*(\w+)\s*$',
            'price': r'💵\s*\$?([\d.]+)',
            'market_cap': r'MC:\s*\$?([\d.]+)([KMB]?)',
            'liquidity': r'LIQ:\s*\$?([\d.]+)([KMB]?)',
            'volume_24h': r'Vol:\s*\$?([\d.]+)([KMB]?)',
            'bundles': r'B:\s*(\d+)%',
            'snipers': r'S:\s*(\d+)%',
            'dev': r'Dev:\s*(\d+)%',
            'confidence': r'Score:\s*(\d+)%',
            'ca': r'📝\s*([A-Za-z0-9]{32,44})'
        }
    },
    
    # Format 3: Simple format (minimal info)
    'simple': {
        'name': 'Simple Format',
        'example': '''
🚀 TOKEN NAME
Solana
$100K MC
Contract: ABC123...XYZ789
        ''',
        'patterns': {
            'token_name': r'^[🚀💎⚡🔥]+\s*([A-Z][A-Za-z0-9\s\-]+)',
            'chain': r'^(Solana|Ethereum|BSC|Base)\s*$',
            'market_cap': r'\$?([\d.]+)([KMB]?)\s*MC',
            'ca': r'(?:Contract|CA|Address):\s*([A-Za-z0-9]{32,44})'
        }
    },
    
    # Format 4: Detailed format with extra metrics
    'detailed': {
        'name': 'Detailed Format',
        'example': '''
🔥 TOKEN NAME (SYMBOL)
⛓️ Chain: Solana
💰 Entry Price: $0.00001
📊 Market Cap: $100K (FDV: $120K)
💧 Liquidity: $50K (Locked: 80%)
📈 Volume 24h: $25K
🎯 Holders: 250
👥 Bundles: 5 (10%)
🎯 Snipers: 3 (5%)
👨‍💻 Dev Holdings: 0%
✅ Confidence Score: 85%
📝 Contract: ABC123...XYZ789
🔗 DexScreener: https://...
        ''',
        'patterns': {
            'token_name': r'^[🔥🚀💎⚡]+\s*([A-Z][A-Za-z0-9\s\-]+)',
            'chain': r'Chain:\s*(\w+)',
            'price': r'(?:Entry )?Price:\s*\$?([\d.]+)',
            'market_cap': r'Market Cap:\s*\$?([\d.]+)([KMB]?)',
            'liquidity': r'Liquidity:\s*\$?([\d.]+)([KMB]?)',
            'volume_24h': r'Volume 24h:\s*\$?([\d.]+)([KMB]?)',
            'bundles': r'Bundles:\s*\d+\s*\((\d+)%\)',
            'snipers': r'Snipers:\s*\d+\s*\((\d+)%\)',
            'dev': r'Dev(?:\s+Holdings)?:\s*(\d+)%',
            'confidence': r'Confidence(?:\s+Score)?:\s*(\d+)%',
            'ca': r'Contract:\s*([A-Za-z0-9]{32,44})'
        }
    },
    
    # Format 5: List format
    'list': {
        'name': 'List Format',
        'example': '''
New Signal: TOKEN NAME
• Chain: Solana
• Price: $0.00001
• MC: $100K
• Liq: $50K
• Vol: $25K
• CA: ABC123...XYZ789
        ''',
        'patterns': {
            'token_name': r'(?:New Signal|Signal):\s*([A-Z][A-Za-z0-9\s\-]+)',
            'chain': r'Chain:\s*(\w+)',
            'price': r'Price:\s*\$?([\d.]+)',
            'market_cap': r'MC:\s*\$?([\d.]+)([KMB]?)',
            'liquidity': r'Liq:\s*\$?([\d.]+)([KMB]?)',
            'volume_24h': r'Vol:\s*\$?([\d.]+)([KMB]?)',
            'ca': r'CA:\s*([A-Za-z0-9]{32,44})'
        }
    }
}

# Channel ID to format mapping
# Add your channel IDs here and assign them a format
CHANNEL_FORMAT_MAPPING = {
    # Example mappings (replace with your actual channel IDs):
    # -1001234567890: 'standard',
    # -1009876543210: 'compact',
    # -1001111111111: 'simple',
    # Add more as needed...
}

# Default format if channel not mapped
DEFAULT_FORMAT = 'standard'

def get_format_for_channel(channel_id):
    """Get the appropriate format configuration for a channel"""
    format_key = CHANNEL_FORMAT_MAPPING.get(channel_id, DEFAULT_FORMAT)
    return CHANNEL_FORMATS.get(format_key, CHANNEL_FORMATS['standard'])
