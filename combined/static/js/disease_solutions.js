// // Function to fetch disease information from multiple sources
// async function fetchDiseaseInfo(diseaseName) {
//     try {
//         // Construct the search query
//         const query = `${diseaseName} plant disease treatment solutions`;
        
//         // Make a request to our backend endpoint that will handle the web scraping
//         const response = await fetch(`/search_disease?query=${encodeURIComponent(query)}`);
//         const data = await response.json();
        
//         return {
//             description: data.description || "Information about this disease is being fetched...",
//             solutions: data.solutions || ["Loading solutions..."],
//             sources: data.sources || []
//         };
//     } catch (error) {
//         console.error('Error fetching disease information:', error);
//         return {
//             description: "Unable to fetch disease information at the moment.",
//             solutions: ["Please try again later"],
//             sources: []
//         };
//     }
// }

// // Function to update the solutions section with loading state
// function showLoadingState(diseaseName) {
//     const solutionsContainer = document.getElementById('diseaseSolutions');
//     solutionsContainer.innerHTML = `
//         <div class="solution-content">
//             <h3>${diseaseName}</h3>
//             <div class="loading-spinner">
//                 <div class="spinner-border text-success" role="status">
//                     <span class="visually-hidden">Loading...</span>
//                 </div>
//             </div>
//             <p>Searching for solutions...</p>
//         </div>
//     `;
// }

// // Function to update the solutions section with fetched data
// function updateDiseaseSolutions(diseaseInfo, diseaseName) {
//     const solutionsContainer = document.getElementById('diseaseSolutions');
    
//     solutionsContainer.innerHTML = `
//         <div class="solution-content">
//             <h3>${diseaseName}</h3>
//             <div class="disease-info-card">
//                 <p class="disease-description">${diseaseInfo.description}</p>
                
//                 <h4 class="mt-4">Recommended Solutions:</h4>
//                 <ul class="solutions-list">
//                     ${diseaseInfo.solutions.map(solution => `
//                         <li class="solution-item">
//                             <i class="fas fa-leaf solution-icon"></i>
//                             ${solution}
//                         </li>
//                     `).join('')}
//                 </ul>

//                 ${diseaseInfo.sources.length > 0 ? `
//                     <div class="sources-section mt-4">
//                         <h5>Sources:</h5>
//                         <ul class="sources-list">
//                             ${diseaseInfo.sources.map(source => `
//                                 <li><a href="${source.url}" target="_blank" rel="noopener noreferrer">${source.title}</a></li>
//                             `).join('')}
//                         </ul>
//                     </div>
//                 ` : ''}
//             </div>
//         </div>
//     `;
// }

// // Initialize when the page loads
// document.addEventListener('DOMContentLoaded', async function() {
//     const diseaseName = document.querySelector('.prediction-label').textContent;
    
//     // Show loading state
//     showLoadingState(diseaseName);
    
//     // Fetch and update with real data
//     const diseaseInfo = await fetchDiseaseInfo(diseaseName);
//     updateDiseaseSolutions(diseaseInfo, diseaseName);
// }); 

document.addEventListener('DOMContentLoaded', async function() {
    // Extract the disease name from the prediction label
    const diseaseNameElement = document.querySelector('.prediction-label');
    if (!diseaseNameElement) {
        console.error("Prediction label not found.");
        return;
    }
    const diseaseName = diseaseNameElement.textContent;
    const solutionsContainer = document.getElementById('diseaseSolutions');

    // 1. Show an immediate loading state
    showLoadingState(diseaseName, solutionsContainer);
    
    // 2. Fetch the disease information from our backend
    const diseaseInfo = await fetchDiseaseInfo(diseaseName);
    
    // 3. Update the UI with the fetched information
    updateDiseaseSolutions(diseaseInfo, diseaseName, solutionsContainer);
});

/**
 * Displays a loading spinner and message in the solutions container.
 * @param {string} diseaseName - The name of the disease being looked up.
 * @param {HTMLElement} container - The container element to update.
 */
function showLoadingState(diseaseName, container) {
    container.innerHTML = `
        <h3 class="h5">${diseaseName}</h3>
        <div class="d-flex align-items-center mt-3">
            <div class="spinner-border text-success" role="status">
                <span class="visually-hidden">Loading...</span>
            </div>
            <strong class="ms-3">Searching for solutions and treatment advice...</strong>
        </div>
    `;
}

/**
 * Fetches disease information from the backend API.
 * @param {string} diseaseName - The name of the disease to query.
 * @returns {Promise<object>} A promise that resolves to the disease information object.
 */
async function fetchDiseaseInfo(diseaseName) {
    try {
        const response = await fetch(`/search_disease?query=${encodeURIComponent(diseaseName)}`);
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        return await response.json();
    } catch (error) {
        console.error('Error fetching disease information:', error);
        return {
            description: "Could not fetch disease information at this moment. Please check your connection or try again later.",
            solutions: ["Unable to retrieve solutions."],
            sources: []
        };
    }
}

/**
 * Updates the solutions container with the fetched disease information.
 * @param {object} diseaseInfo - The disease information object from the API.
 * @param {string} diseaseName - The name of the disease.
 * @param {HTMLElement} container - The container element to update.
 */
function updateDiseaseSolutions(diseaseInfo, diseaseName, container) {
    const solutionsHTML = diseaseInfo.solutions.length > 0 && diseaseInfo.solutions[0] !== "Unable to retrieve solutions."
        ? diseaseInfo.solutions.map(solution => `
            <li class="solution-item">
                <i class="fas fa-leaf solution-icon"></i>
                <div>${solution}</div>
            </li>`).join('')
        : '<li>No specific solutions found. It is recommended to consult a local agricultural expert.</li>';
    
    const sourcesHTML = diseaseInfo.sources.length > 0
        ? diseaseInfo.sources.map(source => `
            <li><a href="${source.url}" target="_blank" rel="noopener noreferrer">${source.title}</a></li>`).join('')
        : '';

    container.innerHTML = `
        <h3 class="h5">${diseaseName}</h3>
        <p class="text-muted">${diseaseInfo.description}</p>
        
        <h4 class="mt-4 h6">Recommended Solutions:</h4>
        <ul class="solutions-list">
            ${solutionsHTML}
        </ul>

        ${sourcesHTML ? `
            <div class="mt-4">
                <h5 class="h6">Sources:</h5>
                <ul class="list-unstyled small">
                    ${sourcesHTML}
                </ul>
            </div>` : ''}
    `;
}
