const axios = require('axios');

const JIRA_BASE_URL = 'https://your-jira-instance.atlassian.net';
const JIRA_BOARD_ID = 'your-board-id';
const JIRA_USERNAME = 'your-email@example.com';
const JIRA_API_TOKEN = 'your-api-token';

async function getRecentIssues() {
    const url = `${JIRA_BASE_URL}/rest/agile/1.0/board/${JIRA_BOARD_ID}/issue?maxResults=10&orderBy=-created`;

    try {
        const response = await axios.get(url, {
            auth: {
                username: JIRA_USERNAME,
                password: JIRA_API_TOKEN
            }
        });

        const issues = response.data.issues;
        console.log('Recent 10 issues:', issues);
    } catch (error) {
        console.error('Error fetching issues:', error);
    }
}

getRecentIssues();
