from django.contrib.auth.models import Permission
from triduum_resource.cross_app.models import AppSection
from django.db.models import Q


def _merge_app_section_trees(sections_trees):
    merged_dict = {}
    for sect in sections_trees:
        if sect[0].id not in merged_dict:
            merged_dict[sect[0].id] = {
                'children': {}
            }
        for idx, opt in enumerate(sect[1:]):
            if idx == 0:
                if opt.id not in merged_dict[sect[0].id]['children']:
                    merged_dict[sect[0].id]['children'][opt.id] = {
                        'children': {}
                        }
            elif idx == 1:
                merged_dict[sect[0].id]['children'][sect[1].id]['children'][opt.id] = {
                    'children': None # Up to than 3 levels in app section
                }
    section_subtree = AppSection.objects.filter(id__in = merged_dict.keys()).order_by('order')
    for section in section_subtree:
        setattr(section, 'children',
            AppSection.objects.filter(
                id__in = merged_dict[section.id]['children'].keys()
                ).order_by('order')
        )
        for child_section in section.children:
            setattr(child_section, 'children',
                AppSection.objects.filter(
                    id__in = merged_dict[
                        section.id][
                            'children'][
                                child_section.id][
                                    'children'].keys()
                    ).order_by('order')
            )
    return section_subtree

def get_user_app_sections_tree(user):
    user_all_perms = Permission.objects.filter(
            Q(group__in=user.groups.all())|Q(user=user)
            ).distinct()
    if user.is_superuser:
        sections_by_perms = AppSection.objects.all()
    else:
        sections_by_perms = AppSection.objects.select_related('parent').filter(
            (Q(app_permission__permission__in=user_all_perms) | 
            Q(app_permission = None)) & Q(admin_required = False)
        )
    app_section_trees = _merge_app_section_trees(
        [x.get_parent_tree() for x in sections_by_perms]
    )
    return app_section_trees