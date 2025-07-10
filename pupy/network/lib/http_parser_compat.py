#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Compatibility layer for http_parser to work with Python 3.13+
This provides a minimal implementation for parsing HTTP responses
"""

import email.parser
import io
from urllib.parse import urlparse


class HttpParser:
    """
    Minimal HTTP parser compatible with http_parser API
    """
    
    def __init__(self, kind=0):
        self.kind = kind  # 0 = request, 1 = response
        self.data = b""
        self.parsed = False
        self._headers = {}
        self._status_code = None
        self._reason = None
        self._body = b""
        
    def execute(self, data, length=None):
        """Execute parsing on data"""
        if length is None:
            length = len(data)
        
        self.data += data[:length]
        self._parse()
        return length
    
    def _parse(self):
        """Parse the accumulated data"""
        if self.parsed:
            return
            
        if b'\r\n\r\n' not in self.data:
            return  # Not enough data yet
            
        header_part, self._body = self.data.split(b'\r\n\r\n', 1)
        header_str = header_part.decode('utf-8', errors='ignore')
        
        lines = header_str.split('\r\n')
        if not lines:
            return
            
        # Parse status line
        if self.kind == 1:  # Response
            status_line = lines[0]
            parts = status_line.split(' ', 2)
            if len(parts) >= 2:
                self._status_code = int(parts[1])
                self._reason = parts[2] if len(parts) > 2 else ""
        
        # Parse headers
        for line in lines[1:]:
            if ':' in line:
                key, value = line.split(':', 1)
                self._headers[key.strip().lower()] = value.strip()
        
        self.parsed = True
    
    def get_headers(self):
        """Get headers as dict"""
        return self._headers
    
    def get_status_code(self):
        """Get status code"""
        return self._status_code
    
    def get_body(self):
        """Get body"""
        return self._body
    
    def is_headers_complete(self):
        """Check if headers are complete"""
        return self.parsed
    
    def is_message_complete(self):
        """Check if message is complete"""
        return self.parsed
    
    def get_url(self):
        """Get URL (for requests)"""
        return ""
    
    def get_method(self):
        """Get method (for requests)"""
        return ""