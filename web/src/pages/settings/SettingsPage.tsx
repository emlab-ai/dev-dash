import SecondaryNavSidebar from "../layouts/SecondaryNavSidebar";

const listItems = [
    {
        text: 'Teams',
        url: '/settings/teams'
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