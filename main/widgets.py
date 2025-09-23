from django import forms
from django.forms.widgets import Widget
from django.forms.utils import flatatt
from django.utils.html import format_html
from django.utils.safestring import mark_safe
import json


class SocialMediaLinksWidget(Widget):
    """
    Custom widget for managing social media links as JSON field.
    Allows up to 5 social media links with Title and URL inputs.
    """
    
    def __init__(self, attrs=None, max_links=5):
        super().__init__(attrs)
        self.max_links = max_links
    
    def format_value(self, value):
        """Convert the JSON value to a format suitable for the widget"""        
        if value is None:
            return []
        if isinstance(value, str):
            try:
                parsed = json.loads(value)
                # Handle both dict and list formats
                if isinstance(parsed, dict):
                    return []  # Convert empty dict to empty list
                elif isinstance(parsed, list):
                    return parsed
                return []
            except (json.JSONDecodeError, TypeError):
                return []
        if isinstance(value, dict):
            return []  # Convert dict to empty list (legacy data)
        if isinstance(value, list):
            return value
        # Handle slice objects (Django sometimes passes these)
        if hasattr(value, '__getitem__') and hasattr(value, 'stop'):
            return []
        # Handle any other unexpected types
        return []
    
    def render(self, name, value, attrs=None, renderer=None):
        """Render the widget as dynamic social media links with Add/Remove functionality"""
        if attrs is None:
            attrs = {}
        
        # Get the formatted value and ensure it's always a list
        try:
            formatted_value = self.format_value(value)
            if not isinstance(formatted_value, list):
                formatted_value = []
        except Exception:
            formatted_value = []
        
        # Create HTML for the widget
        html_parts = []
        
        # Add container div (no duplicate label - form will handle labeling)
        html_parts.append(f'<div class="social-media-links-widget" data-max-links="{self.max_links}" data-name="{name}">')
        html_parts.append('<div class="social-links-container">')
        
        # Add existing links (only if there are any)
        try:
            for i, link_data in enumerate(formatted_value[:self.max_links]):
                title = link_data.get('title', '') if isinstance(link_data, dict) else ''
                url = link_data.get('url', '') if isinstance(link_data, dict) else ''
                html_parts.append(self._render_link_pair(name, i, title, url, show_remove=True))
        except Exception:
            # If there's any error with the data, just show an empty form
            pass
        
        # If no existing links, show one empty row
        if not formatted_value:
            html_parts.append(self._render_link_pair(name, 0, '', '', show_remove=False))
        
        html_parts.append('</div>')
        
        # Add "Add Link" button (will be shown/hidden by JavaScript)
        # Start visible by default, let JavaScript handle the logic
        button_style = 'margin-top: 10px;'
        html_parts.append(f'<button type="button" class="btn btn-outline-primary btn-sm add-link-btn" style="{button_style}">+ Add Social Media Link</button>')
        
        # Add hidden input to store the JSON value
        hidden_attrs = {'type': 'hidden', 'name': name, 'id': attrs.get('id', '')}
        if formatted_value:
            hidden_attrs['value'] = json.dumps(formatted_value)
        else:
            hidden_attrs['value'] = '[]'
        html_parts.append(format_html('<input{}>', flatatt(hidden_attrs)))
        
        # Add JavaScript for dynamic behavior
        html_parts.append(self._render_javascript())
        
        html_parts.append('</div>')
        
        return mark_safe(''.join(html_parts))
    
    def _render_link_pair(self, name, index, title, url, show_remove=False):
        """Render a single title-url pair with optional remove button"""
        remove_button = ''
        if show_remove:
            remove_button = '''
                <div class="col-auto">
                    <button type="button" class="btn btn-outline-danger btn-sm remove-link-btn" 
                            data-index="{}">×</button>
                </div>
            '''.format(index)
        
        return format_html('''
            <div class="row mb-2 social-link-pair" data-index="{}" style="{}">
                <div class="col-md-4 col-lg-3">
                    <input type="text" class="form-control social-title" 
                           placeholder="Platform (e.g. LinkedIn)" 
                           value="{}" data-name="{}" data-index="{}">
                </div>
                <div class="col-md-7 col-lg-8">
                    <input type="url" class="form-control social-url" 
                           placeholder="https://example.com/profile" 
                           value="{}" data-name="{}" data-index="{}">
                </div>
                {}
            </div>
        ''', 
        index, 
        'display: none;' if not title and not url and index > 0 else '',
        title, name, index, 
        url, name, index,
        remove_button)
    
    def _render_javascript(self):
        """Render JavaScript for dynamic Add/Remove functionality"""
        return format_html('''
            <script>
            // Global event delegation approach - more reliable for AJAX content
            (function() {{
                // Only set up global listeners once
                if (window.socialMediaWidgetInitialized) {{
                    return;
                }}
                window.socialMediaWidgetInitialized = true;
                
                console.log('� Setting up global social media widget handlers');
                
                // Global click handler for add buttons
                document.addEventListener('click', function(e) {{
                    if (e.target.classList.contains('add-link-btn')) {{
                        console.log('� Add link button clicked via delegation');
                        e.preventDefault();
                        e.stopPropagation();
                        
                        const widget = e.target.closest('.social-media-links-widget');
                        if (widget) {{
                            addNewLinkToWidget(widget);
                        }}
                        return false;
                    }}
                    
                    if (e.target.classList.contains('remove-link-btn')) {{
                        console.log('🟢 Remove link button clicked via delegation');
                        e.preventDefault();
                        e.stopPropagation();
                        
                        const widget = e.target.closest('.social-media-links-widget');
                        const index = e.target.dataset.index;
                        if (widget && index !== undefined) {{
                            removeLinkFromWidget(widget, index);
                        }}
                        return false;
                    }}
                }});
                
                // Global input handler for social media fields
                document.addEventListener('input', function(e) {{
                    if (e.target.classList.contains('social-title') || e.target.classList.contains('social-url')) {{
                        const widget = e.target.closest('.social-media-links-widget');
                        if (widget) {{
                            updateWidgetState(widget);
                        }}
                    }}
                }});
                
                // Global change handler
                document.addEventListener('change', function(e) {{
                    if (e.target.classList.contains('social-title') || e.target.classList.contains('social-url')) {{
                        const widget = e.target.closest('.social-media-links-widget');
                        if (widget) {{
                            updateWidgetState(widget);
                        }}
                    }}
                }});
                
                function addNewLinkToWidget(widget) {{
                    console.log('🟢 Adding new link to widget');
                    const socialContainer = widget.querySelector('.social-links-container');
                    const maxLinks = parseInt(widget.dataset.maxLinks);
                    const fieldName = widget.dataset.name;
                    
                    if (!socialContainer) return;
                    
                    const existingPairs = socialContainer.querySelectorAll('.social-link-pair');
                    if (existingPairs.length >= maxLinks) {{
                        console.log('🟡 Max links reached');
                        return;
                    }}
                    
                    const nextIndex = existingPairs.length;
                    const newPair = document.createElement('div');
                    newPair.className = 'row mb-2 social-link-pair';
                    newPair.dataset.index = nextIndex;
                    newPair.innerHTML = `
                        <div class="col-md-4 col-lg-3">
                            <input type="text" class="form-control social-title" 
                                   placeholder="Platform (e.g. LinkedIn)" 
                                   value="" data-name="${{fieldName}}" data-index="${{nextIndex}}">
                        </div>
                        <div class="col-md-7 col-lg-8">
                            <input type="url" class="form-control social-url" 
                                   placeholder="https://example.com/profile" 
                                   value="" data-name="${{fieldName}}" data-index="${{nextIndex}}">
                        </div>
                        <div class="col-auto">
                            <button type="button" class="btn btn-outline-danger btn-sm remove-link-btn" 
                                    data-index="${{nextIndex}}">×</button>
                        </div>
                    `;
                    
                    socialContainer.appendChild(newPair);
                    console.log('🟢 New link pair added');
                    
                    // Focus on new title input
                    const newTitleInput = newPair.querySelector('.social-title');
                    if (newTitleInput) {{
                        newTitleInput.focus();
                    }}
                    
                    updateWidgetState(widget);
                }}
                
                function removeLinkFromWidget(widget, index) {{
                    console.log('🔴 Removing link from widget, index:', index);
                    const socialContainer = widget.querySelector('.social-links-container');
                    if (!socialContainer) return;
                    
                    const pair = socialContainer.querySelector(`.social-link-pair[data-index="${{index}}"]`);
                    if (pair) {{
                        pair.remove();
                        updateWidgetIndices(widget);
                        updateWidgetState(widget);
                        console.log('🔴 Link pair removed');
                    }}
                }}
                
                function updateWidgetIndices(widget) {{
                    const socialContainer = widget.querySelector('.social-links-container');
                    if (!socialContainer) return;
                    
                    const pairs = socialContainer.querySelectorAll('.social-link-pair');
                    pairs.forEach((pair, index) => {{
                        pair.dataset.index = index;
                        const titleInput = pair.querySelector('.social-title');
                        const urlInput = pair.querySelector('.social-url');
                        const removeBtn = pair.querySelector('.remove-link-btn');
                        
                        if (titleInput) titleInput.dataset.index = index;
                        if (urlInput) urlInput.dataset.index = index;
                        if (removeBtn) removeBtn.dataset.index = index;
                    }});
                }}
                
                function updateWidgetState(widget) {{
                    const socialContainer = widget.querySelector('.social-links-container');
                    const hiddenInput = widget.querySelector('input[type="hidden"]');
                    const addButton = widget.querySelector('.add-link-btn');
                    const maxLinks = parseInt(widget.dataset.maxLinks);
                    
                    if (!socialContainer || !hiddenInput || !addButton) return;
                    
                    // Update hidden input with current data
                    const links = [];
                    const pairs = socialContainer.querySelectorAll('.social-link-pair');
                    
                    pairs.forEach(pair => {{
                        const titleInput = pair.querySelector('.social-title');
                        const urlInput = pair.querySelector('.social-url');
                        
                        if (titleInput && urlInput) {{
                            const title = titleInput.value.trim();
                            const url = urlInput.value.trim();
                            
                            if (title && url) {{
                                links.push({{ title: title, url: url }});
                            }}
                        }}
                    }});
                    
                    hiddenInput.value = JSON.stringify(links);
                    
                    // Update button visibility
                    const visiblePairs = Array.from(pairs).filter(pair => {{
                        const style = window.getComputedStyle(pair);
                        return style.display !== 'none';
                    }});
                    
                    // Hide if max links reached
                    if (visiblePairs.length >= maxLinks) {{
                        addButton.style.display = 'none';
                        return;
                    }}
                    
                    // For single pair, show button only when both fields filled
                    if (visiblePairs.length === 1) {{
                        const firstPair = visiblePairs[0];
                        const titleInput = firstPair.querySelector('.social-title');
                        const urlInput = firstPair.querySelector('.social-url');
                        
                        if (titleInput && urlInput) {{
                            const title = titleInput.value.trim();
                            const url = urlInput.value.trim();
                            const bothFilled = title && url;
                            
                            addButton.style.display = bothFilled ? 'inline-block' : 'none';
                            return;
                        }}
                    }}
                    
                    // For multiple pairs, show button only when all are filled
                    let allComplete = true;
                    visiblePairs.forEach(pair => {{
                        const titleInput = pair.querySelector('.social-title');
                        const urlInput = pair.querySelector('.social-url');
                        
                        if (titleInput && urlInput) {{
                            const title = titleInput.value.trim();
                            const url = urlInput.value.trim();
                            if (!title || !url) {{
                                allComplete = false;
                            }}
                        }}
                    }});
                    
                    addButton.style.display = allComplete ? 'inline-block' : 'none';
                }}
                
                // Initialize any existing widgets on page load
                function initializeExistingWidgets() {{
                    const widgets = document.querySelectorAll('.social-media-links-widget[data-max-links="{}"]');
                    console.log('🟢 Initializing', widgets.length, 'existing widgets');
                    widgets.forEach(widget => {{
                        updateWidgetIndices(widget);
                        updateWidgetState(widget);
                    }});
                }}
                
                // Set up initialization functions
                window.initializeSocialMediaWidget = function(container) {{
                    console.log('🟢 initializeSocialMediaWidget called (delegation mode)');
                    if (container) {{
                        const widgets = container.querySelectorAll('.social-media-links-widget[data-max-links="{}"]');
                        widgets.forEach(widget => {{
                            updateWidgetIndices(widget);
                            updateWidgetState(widget);
                        }});
                    }} else {{
                        initializeExistingWidgets();
                    }}
                }};
                
                // Initialize on DOM ready
                if (document.readyState === 'loading') {{
                    document.addEventListener('DOMContentLoaded', initializeExistingWidgets);
                }} else {{
                    initializeExistingWidgets();
                }}
            }})();
            </script>
        ''', self.max_links, self.max_links)


class SocialMediaLinksField(forms.JSONField):
    """
    Custom form field for social media links with validation.
    """
    
    widget = SocialMediaLinksWidget
    
    def __init__(self, max_links=5, *args, **kwargs):
        self.max_links = max_links
        kwargs.setdefault('widget', SocialMediaLinksWidget(max_links=max_links))
        super().__init__(*args, **kwargs)
    
    def clean(self, value):
        """Clean and validate the social media links data"""
        if not value:
            return []
        
        # If it's a string, try to parse it as JSON
        if isinstance(value, str):
            try:
                value = json.loads(value)
            except (json.JSONDecodeError, TypeError):
                raise forms.ValidationError("Invalid JSON format for social media links.")
        
        # Ensure it's a list
        if not isinstance(value, list):
            raise forms.ValidationError("Social media links must be a list.")
        
        # Validate each link
        cleaned_links = []
        for i, link in enumerate(value[:self.max_links]):
            if not isinstance(link, dict):
                continue
                
            title = link.get('title', '').strip()
            url = link.get('url', '').strip()
            
            if title and url:
                # Basic URL validation
                if not url.startswith(('http://', 'https://')):
                    raise forms.ValidationError(f"Link {i+1}: URL must start with http:// or https://")
                
                cleaned_links.append({
                    'title': title,
                    'url': url
                })
        
        return cleaned_links
    
    def widget_attrs(self, widget):
        """Add max_links attribute to widget"""
        attrs = super().widget_attrs(widget)
        attrs['data-max-links'] = self.max_links
        return attrs
