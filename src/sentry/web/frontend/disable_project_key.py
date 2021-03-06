from __future__ import absolute_import

from django.contrib import messages
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _

from sentry.models import AuditLogEntryEvent, ProjectKey, ProjectKeyStatus
from sentry.web.frontend.base import ProjectView


class DisableProjectKeyView(ProjectView):
    required_scope = 'project:write'

    def post(self, request, organization, team, project, key_id):
        try:
            key = ProjectKey.objects.get(
                project=project,
                id=key_id,
            )
        except ProjectKey.DoesNotExist:
            return self.redirect(reverse('sentry-manage-project-keys', args=[project.organization.slug, project.slug]))

        key.update(status=ProjectKeyStatus.INACTIVE)

        self.create_audit_entry(
            request,
            organization=organization,
            target_object=key.id,
            event=AuditLogEntryEvent.PROJECTKEY_DISABLE,
            data=key.get_audit_log_data(),
        )

        messages.add_message(
            request, messages.SUCCESS,
            _('The API key (%s) was disabled.') % (key.public_key,))

        return self.redirect(reverse('sentry-manage-project-keys', args=[project.organization.slug, project.slug]))
