// Publications data and functionality
let allPublications = [];
let filteredPublications = [];

/** Escape text for safe use in HTML text content (prevents XSS). */
function escapeHtml(str) {
	if (str == null) return '';
	const div = document.createElement('div');
	div.textContent = str;
	return div.innerHTML;
}

/** Return publication authors array (safe for missing/malformed data). */
function getAuthors(pub) {
	return Array.isArray(pub.authors) ? pub.authors : [];
}

function getPublicationYear(pub) {
	return Number(pub.issued_year || pub.year || 0);
}

function updatePublicationActions() {
	const searchInput = document.getElementById('search-input');
	const typeFilter = document.getElementById('type-filter');
	const yearFilter = document.getElementById('year-filter');
	const sortBy = document.getElementById('sort-by');
	const clearButton = document.getElementById('clear-filters');
	const exportButton = document.getElementById('export-json');
	const exportCount = document.getElementById('export-count');

	const hasActiveControls = Boolean(
		searchInput.value.trim() ||
		typeFilter.value ||
		yearFilter.value ||
		sortBy.value !== 'year-desc'
	);
	const resultCount = filteredPublications.length;

	clearButton.disabled = !hasActiveControls;
	exportButton.disabled = resultCount === 0;
	exportButton.setAttribute(
		'aria-label',
		`Export ${resultCount} filtered publication${resultCount === 1 ? '' : 's'} as JSON`
	);
	exportCount.textContent = `${resultCount} ${resultCount === 1 ? 'record' : 'records'}`;
}

/** True if keyboard events should not run page shortcuts (user is typing elsewhere). */
function isTypingContext(el) {
	if (!el) return false;
	if (el.isContentEditable) return true;
	const tag = el.tagName ? el.tagName.toLowerCase() : '';
	if (tag === 'input' || tag === 'textarea' || tag === 'select') return true;
	return el.closest && el.closest('[contenteditable="true"]');
}

// Load publications data
async function loadPublications() {
	try {
		const response = await fetch('data.json?v=20260807');
		const data = await response.json();
		allPublications = data.publications || [];
		filteredPublications = [...allPublications];
		
		updateStats();
		populateYearFilter();
		displayPublications();
		updatePublicationActions();
	} catch (error) {
		console.error('Error loading publications:', error);
		document.getElementById('publications-container').innerHTML = 
			'<div class="no-results">Error loading publications. Please try again later.</div>';
	}
}

// Update statistics
function updateStats() {
	const totalPubs = allPublications.length;
	const papers = allPublications.filter(pub => isPaper(pub)).length;
	const patents = allPublications.filter(pub => isPatent(pub)).length;
	const totalCitations = allPublications.reduce((sum, pub) => sum + (pub.cited_by || 0), 0);
	
	document.getElementById('total-pubs').textContent = totalPubs;
	document.getElementById('papers').textContent = papers;
	document.getElementById('patents').textContent = patents;
	document.getElementById('citations').textContent = totalCitations;
	document.getElementById('publications-stats').style.display = 'flex';
}

// Populate year filter
function populateYearFilter() {
	const years = [...new Set(allPublications.map(getPublicationYear).filter(year => year > 0))].sort((a, b) => b - a);
	const yearFilter = document.getElementById('year-filter');
	
	years.forEach(year => {
		const option = document.createElement('option');
		option.value = year;
		option.textContent = year;
		yearFilter.appendChild(option);
	});
}

// Determine publication type (safe for missing title/snippet).
function getPublicationType(pub) {
	if (pub && ['paper', 'patent', 'report'].includes(pub.type)) return pub.type;
	const title = (pub.title != null) ? String(pub.title).toLowerCase() : '';
	
	if (title.includes('patent')) {
		return 'patent';
	} else if (pub.venue && (pub.venue.includes('arXiv') || pub.venue.includes('preprint'))) {
		return 'report';
	} else {
		return 'paper';
	}
}

function isPaper(pub) {
	return getPublicationType(pub) === 'paper';
}

function isPatent(pub) {
	return getPublicationType(pub) === 'patent';
}

// Filter publications
function filterPublications() {
	const searchTerm = document.getElementById('search-input').value.toLowerCase();
	const typeFilter = document.getElementById('type-filter').value;
	const yearFilter = document.getElementById('year-filter').value;
	const sortBy = document.getElementById('sort-by').value;
	
	filteredPublications = allPublications.filter(pub => {
		// Search filter
		const matchesSearch = !searchTerm ||
			(pub.title && pub.title.toLowerCase().includes(searchTerm)) ||
			getAuthors(pub).some(author => String(author).toLowerCase().includes(searchTerm)) ||
			(pub.venue && pub.venue.toLowerCase().includes(searchTerm)) ||
			(pub.snippet && pub.snippet.toLowerCase().includes(searchTerm));
		
		// Type filter
		const matchesType = !typeFilter || getPublicationType(pub) === typeFilter;
		
		// Year filter
		const matchesYear = !yearFilter || getPublicationYear(pub) == yearFilter;
		
		return matchesSearch && matchesType && matchesYear;
	});
	
	// Sort publications
	sortPublications(sortBy);
	
	displayPublications();
	updatePublicationActions();
}

// Sort publications
function sortPublications(sortBy) {
	switch(sortBy) {
		case 'year-desc':
			filteredPublications.sort((a, b) => getPublicationYear(b) - getPublicationYear(a));
			break;
		case 'year-asc':
			filteredPublications.sort((a, b) => getPublicationYear(a) - getPublicationYear(b));
			break;
		case 'citations-desc':
			filteredPublications.sort((a, b) => (b.cited_by || 0) - (a.cited_by || 0));
			break;
		case 'citations-asc':
			filteredPublications.sort((a, b) => (a.cited_by || 0) - (b.cited_by || 0));
			break;
		case 'title':
			filteredPublications.sort((a, b) => (a.title || '').localeCompare(b.title || ''));
			break;
	}
}

// Display publications
function displayPublications() {
	const container = document.getElementById('publications-container');
	
	if (filteredPublications.length === 0) {
		container.innerHTML = '<div class="no-results">No publications found matching your criteria.</div>';
		return;
	}
	
	const publicationsHTML = filteredPublications.map(pub => {
		const type = getPublicationType(pub);
		const typeClass = type === 'patent' ? 'patent' : type === 'paper' ? 'paper' : 'report';
		const authors = getAuthors(pub);
		const title = escapeHtml(pub.title || '');
		const authorsStr = authors.map(escapeHtml).join(', ');
		const venue = pub.venue ? escapeHtml(pub.venue) : '';
		const snippet = pub.snippet ? escapeHtml(pub.snippet.substring(0, 200)) + (pub.snippet.length > 200 ? '...' : '') : '';
		const year = getPublicationYear(pub);
		return `
			<div class="publication-item">
				<div class="publication-title">${title}</div>
				<div class="publication-authors">${authorsStr}</div>
				${venue ? `<div class="publication-venue">${venue}</div>` : ''}
				<div class="publication-meta">
					${year ? `<span class="publication-year">${year}</span>` : ''}
					${(pub.cited_by || 0) > 0 ? `<span class="publication-citations">${escapeHtml(String(pub.cited_by))} citations</span>` : ''}
					<span class="publication-type ${typeClass}">${type.toUpperCase()}</span>
				</div>
				${snippet ? `<div class="publication-snippet">${snippet}</div>` : ''}
			</div>
		`;
	}).join('');
	
	container.innerHTML = publicationsHTML;
}

// Clear filters
function clearFilters() {
	document.getElementById('search-input').value = '';
	document.getElementById('type-filter').value = '';
	document.getElementById('year-filter').value = '';
	document.getElementById('sort-by').value = 'year-desc';
	filterPublications();
}

// Export JSON
function exportJSON() {
	const dataStr = JSON.stringify(filteredPublications, null, 2);
	const dataBlob = new Blob([dataStr], {type: 'application/json'});
	const url = URL.createObjectURL(dataBlob);
	const link = document.createElement('a');
	link.href = url;
	link.download = 'publications_filtered.json';
	link.click();
	URL.revokeObjectURL(url);
}

// Event listeners
document.addEventListener('DOMContentLoaded', function() {
	loadPublications();
	updatePublicationActions();
	
	document.getElementById('search-input').addEventListener('input', filterPublications);
	document.getElementById('type-filter').addEventListener('change', filterPublications);
	document.getElementById('year-filter').addEventListener('change', filterPublications);
	document.getElementById('sort-by').addEventListener('change', filterPublications);
	document.getElementById('clear-filters').addEventListener('click', clearFilters);
	document.getElementById('export-json').addEventListener('click', exportJSON);
	
	// Keyboard shortcuts (avoid Cmd/Ctrl+F and Cmd/Ctrl+R so browser Find and Reload still work)
	document.addEventListener('keydown', function(e) {
		// / — focus search (skip in other fields; allow "/" inside the search box)
		if (e.key === '/' && !e.ctrlKey && !e.metaKey && !e.altKey) {
			const t = e.target;
			if (t && t.id === 'search-input') return;
			if (isTypingContext(e.target)) return;
			e.preventDefault();
			document.getElementById('search-input').focus();
			return;
		}
		// Ctrl+Shift+L / Cmd+Shift+L — clear filters (still works from selects; not in other text fields)
		if ((e.ctrlKey || e.metaKey) && e.shiftKey && e.key.toLowerCase() === 'l') {
			const t = e.target;
			if (t) {
				if (t.isContentEditable) return;
				const tag = t.tagName ? t.tagName.toLowerCase() : '';
				if (tag === 'textarea') return;
				if (tag === 'input' && t.id !== 'search-input') return;
			}
			e.preventDefault();
			clearFilters();
		}
	});
	
	// Add search highlighting
	document.getElementById('search-input').addEventListener('input', function() {
		const searchTerm = this.value.toLowerCase();
		const items = document.querySelectorAll('.publication-item');
		
		items.forEach(item => {
			const title = item.querySelector('.publication-title').textContent.toLowerCase();
			const authors = item.querySelector('.publication-authors').textContent.toLowerCase();
			const venue = item.querySelector('.publication-venue')?.textContent.toLowerCase() || '';
			
			if (searchTerm && (title.includes(searchTerm) || authors.includes(searchTerm) || venue.includes(searchTerm))) {
				item.classList.add('highlight');
			} else {
				item.classList.remove('highlight');
			}
		});
	});
});
