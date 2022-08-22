from .base import Base


class Ldap(Base):
    def get_ldap_groups(self, params=None):
        """Returns a list of LDAP groups

        q: Search term
        page: The page to select.
        per_page: The number of users per page. There is a maximum limit of 200 users per page.
        """
        return self.client.get("""/ldap/groups""", params=params)

    def link_ldap_group(self, remote_id):
        """Link a LDAP group

        remote_id: Group GUID
        """
        return self.client.post(f"/ldap/groups/{remote_id}/link")