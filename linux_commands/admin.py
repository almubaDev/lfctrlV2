from django.contrib import admin

from .models import CommandFlag, CommandTag, LinuxCommand


class CommandFlagInline(admin.TabularInline):
    model = CommandFlag
    extra = 0


@admin.register(LinuxCommand)
class LinuxCommandAdmin(admin.ModelAdmin):
    list_display = ('owner', 'description', 'command', 'created_at', 'updated_at')
    list_filter = ('owner', 'tags')
    search_fields = ('description', 'command')
    inlines = [CommandFlagInline]


@admin.register(CommandTag)
class CommandTagAdmin(admin.ModelAdmin):
    search_fields = ('name',)


admin.site.register(CommandFlag)
