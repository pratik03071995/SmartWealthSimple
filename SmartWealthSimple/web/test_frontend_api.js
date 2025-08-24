// Test script to verify API calls work from frontend
async function testSectorsAPI() {
    console.log('Testing sectors API...');
    try {
        const response = await fetch('http://127.0.0.1:5001/api/ai/sectors');
        console.log('Response status:', response.status);
        console.log('Response headers:', response.headers);
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        console.log('Sectors data:', data);
        
        if (data.sectors && Array.isArray(data.sectors)) {
            console.log('✅ Sectors API working correctly');
            console.log('Number of sectors:', data.sectors.length);
            data.sectors.forEach(sector => {
                console.log(`- ${sector.name}: ${sector.description}`);
            });
        } else {
            console.log('❌ Invalid sectors data format');
        }
    } catch (error) {
        console.error('❌ Sectors API error:', error);
    }
}

async function testSubsectorsAPI() {
    console.log('\nTesting subsectors API...');
    try {
        const response = await fetch('http://127.0.0.1:5001/api/ai/sectors/Technology/subsectors');
        console.log('Response status:', response.status);
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        console.log('Subsectors data:', data);
        
        if (data.subsectors && Array.isArray(data.subsectors)) {
            console.log('✅ Subsectors API working correctly');
            console.log('Number of subsectors:', data.subsectors.length);
            data.subsectors.forEach(subsector => {
                console.log(`- ${subsector}`);
            });
        } else {
            console.log('❌ Invalid subsectors data format');
        }
    } catch (error) {
        console.error('❌ Subsectors API error:', error);
    }
}

// Run tests
console.log('Starting API tests...');
testSectorsAPI().then(() => {
    return testSubsectorsAPI();
}).then(() => {
    console.log('\n✅ All tests completed');
}).catch(error => {
    console.error('❌ Test failed:', error);
});
