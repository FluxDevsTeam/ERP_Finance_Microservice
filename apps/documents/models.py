from django.db import models


class DocumentCategory(models.Model):
    """Document classification categories"""
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=20, unique=True)
    parent = models.ForeignKey(
        'self',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='subcategories'
    )
    description = models.TextField(blank=True)
    metadata_schema = models.JSONField(default=dict)  # Required metadata fields
    retention_period = models.IntegerField(null=True)  # Days
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['name']


class Document(models.Model):
    """Document master records"""
    document_number = models.CharField(max_length=50, unique=True)
    title = models.CharField(max_length=200)
    category = models.ForeignKey(DocumentCategory, on_delete=models.PROTECT)
    description = models.TextField(blank=True)
    version = models.CharField(max_length=20)
    author = models.UUIDField()
    status = models.CharField(
        max_length=20,
        choices=[
            ('draft', 'Draft'),
            ('pending_review', 'Pending Review'),
            ('approved', 'Approved'),
            ('published', 'Published'),
            ('archived', 'Archived'),
            ('obsolete', 'Obsolete')
        ],
        default='draft'
    )
    file_type = models.CharField(max_length=50)
    file_size = models.BigIntegerField()  # In bytes
    file_path = models.CharField(max_length=500)
    checksum = models.CharField(max_length=64)  # SHA-256 hash
    metadata = models.JSONField(default=dict)
    tags = models.JSONField(default=list)
    expiry_date = models.DateField(null=True)
    is_confidential = models.BooleanField(default=False)
    is_template = models.BooleanField(default=False)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ['-created_at']


class DocumentVersion(models.Model):
    """Document version history"""
    document = models.ForeignKey(
        Document,
        on_delete=models.PROTECT,
        related_name='versions'
    )
    version_number = models.CharField(max_length=20)
    changes = models.TextField()
    author = models.UUIDField()
    file_size = models.BigIntegerField()
    file_path = models.CharField(max_length=500)
    checksum = models.CharField(max_length=64)
    metadata = models.JSONField(default=dict)
    is_current = models.BooleanField(default=False)

    class Meta:
        unique_together = ['document', 'version_number']
        ordering = ['-created_at']


class DocumentWorkflow(models.Model):
    """Document approval and review workflows"""
    name = models.CharField(max_length=100)
    description = models.TextField()
    category = models.ForeignKey(
        DocumentCategory,
        on_delete=models.PROTECT,
        null=True
    )
    steps = models.JSONField()  # Ordered list of approval steps
    is_active = models.BooleanField(default=True)
    sla_days = models.IntegerField(default=7)  # Days to complete workflow
    notifications = models.JSONField(default=dict)  # Notification settings

    class Meta:
        ordering = ['name']


class DocumentApproval(models.Model):
    """Document approval process tracking"""
    document = models.ForeignKey(Document, on_delete=models.PROTECT)
    workflow = models.ForeignKey(DocumentWorkflow, on_delete=models.PROTECT)
    current_step = models.IntegerField(default=0)
    status = models.CharField(
        max_length=20,
        choices=[
            ('pending', 'Pending'),
            ('in_progress', 'In Progress'),
            ('approved', 'Approved'),
            ('rejected', 'Rejected'),
            ('cancelled', 'Cancelled')
        ],
        default='pending'
    )
    due_date = models.DateField()
    completed_date = models.DateField(null=True)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ['-created_at']


class ApprovalStep(models.Model):
    """Individual approval steps"""
    approval = models.ForeignKey(
        DocumentApproval,
        on_delete=models.PROTECT,
        related_name='steps'
    )
    step_number = models.IntegerField()
    approver = models.UUIDField()
    status = models.CharField(
        max_length=20,
        choices=[
            ('pending', 'Pending'),
            ('approved', 'Approved'),
            ('rejected', 'Rejected'),
            ('skipped', 'Skipped')
        ],
        default='pending'
    )
    comments = models.TextField(blank=True)
    action_date = models.DateTimeField(null=True)

    class Meta:
        unique_together = ['approval', 'step_number']
        ordering = ['approval', 'step_number']


class DocumentShare(models.Model):
    """Document sharing and permissions"""
    document = models.ForeignKey(Document, on_delete=models.PROTECT)
    shared_with = models.UUIDField()  # User or Group ID
    share_type = models.CharField(
        max_length=20,
        choices=[
            ('user', 'User'),
            ('group', 'Group'),
            ('role', 'Role')
        ]
    )
    permissions = models.JSONField()  # read, write, share, etc.
    expiry_date = models.DateTimeField(null=True)
    shared_by = models.UUIDField()
    is_active = models.BooleanField(default=True)
    notes = models.TextField(blank=True)

    class Meta:
        unique_together = ['document', 'shared_with', 'share_type']
        ordering = ['document', '-created_at']


class DocumentAudit(models.Model):
    """Document activity audit trail"""
    document = models.ForeignKey(Document, on_delete=models.PROTECT)
    action = models.CharField(
        max_length=20,
        choices=[
            ('create', 'Created'),
            ('update', 'Updated'),
            ('delete', 'Deleted'),
            ('view', 'Viewed'),
            ('download', 'Downloaded'),
            ('share', 'Shared'),
            ('approve', 'Approved'),
            ('reject', 'Rejected'),
            ('archive', 'Archived')
        ]
    )
    user = models.UUIDField()
    ip_address = models.GenericIPAddressField(null=True)
    user_agent = models.CharField(max_length=500, blank=True)
    details = models.JSONField(default=dict)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ['-created_at']


class Template(models.Model):
    """Document templates"""
    name = models.CharField(max_length=100)
    description = models.TextField()
    category = models.ForeignKey(DocumentCategory, on_delete=models.PROTECT)
    file_path = models.CharField(max_length=500)
    file_type = models.CharField(max_length=50)
    variables = models.JSONField(default=list)  # Template variables
    default_values = models.JSONField(default=dict)
    is_active = models.BooleanField(default=True)
    version = models.CharField(max_length=20)
    author = models.UUIDField()
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ['name', '-version']


class RetentionPolicy(models.Model):
    """Document retention policies"""
    name = models.CharField(max_length=100)
    description = models.TextField()
    category = models.ForeignKey(
        DocumentCategory,
        on_delete=models.PROTECT,
        null=True
    )
    retention_period = models.IntegerField()  # Days
    action = models.CharField(
        max_length=20,
        choices=[
            ('archive', 'Archive'),
            ('delete', 'Delete'),
            ('review', 'Review Required')
        ]
    )
    notification_days = models.IntegerField()  # Days before action
    is_active = models.BooleanField(default=True)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ['name']


class DocumentRequest(models.Model):
    """Document access requests"""
    document = models.ForeignKey(Document, on_delete=models.PROTECT)
    requested_by = models.UUIDField()
    purpose = models.TextField()
    access_type = models.CharField(
        max_length=20,
        choices=[
            ('read', 'Read'),
            ('write', 'Write'),
            ('admin', 'Admin')
        ]
    )
    status = models.CharField(
        max_length=20,
        choices=[
            ('pending', 'Pending'),
            ('approved', 'Approved'),
            ('rejected', 'Rejected'),
            ('cancelled', 'Cancelled')
        ],
        default='pending'
    )
    approved_by = models.UUIDField(null=True)
    approval_date = models.DateTimeField(null=True)
    valid_until = models.DateTimeField(null=True)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ['-created_at']