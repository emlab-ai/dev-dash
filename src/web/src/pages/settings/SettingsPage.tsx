import SecondaryNavSidebar from "../layouts/SecondaryNavSidebar";

const listItems = [
    {
        text: 'Organization',
        url: '/settings/organisation'
    },
    {
        text: 'Teams',
        url: '/settings/teams'
    },
    {
        text: 'Repositories',
        url: '/settings/repositories'
    },
    {
        text: 'Users',
        url: '/settings/users'
    }
];
function SettingsPage() {
    return (
        <SecondaryNavSidebar items={listItems}/>
    );
}

export default SettingsPage;