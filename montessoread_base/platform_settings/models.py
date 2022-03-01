import datetime
from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import gettext as _
from triduum_resource.cross_app.models import Base
from classroom.models import Student
from courses_management.models import Exercise
# Create your models here.


class Subscription(Base):

    clear_cache = True

    name = models.CharField(_('Name'), max_length=100)
    description = models.TextField(null=True, blank=True)
    students_number = models.PositiveSmallIntegerField(_('Students number'))
    days_term = models.PositiveSmallIntegerField(_('Days term'))

    def __str__(self):
        return str(self.name)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['disabled', 'name'], #todo: order?
                name="unique_together_subscriptions")
        ]

class SubscriptionExercise(Base):

    subscription = models.ForeignKey(Subscription, verbose_name=_('Subscription'), on_delete=models.CASCADE)
    exercise = models.ForeignKey(Exercise, verbose_name=_('Student'), on_delete=models.CASCADE)

    class Meta:
        verbose_name = _("Subscription exercise")
        verbose_name_plural = _("Subscriptions exercise")

    def __str__(self):
        return "{} - {}".format(str(self.subscription.id), str(self.exercise.id))

class UserSubscription(Base):

    name = models.CharField(verbose_name=_('Name'), max_length=100)
    user = models.ForeignKey(User, verbose_name=_('User'), on_delete=models.CASCADE)
    subscription = models.ForeignKey(Subscription, verbose_name=_('Subscription'), on_delete=models.CASCADE)
    start_date = models.DateTimeField(_('Start date'), null = True)
    end_date = models.DateTimeField(_('Start date'), null = True)
    students = models.ManyToManyField(
        Student,
        through='StudentSubscription',
        through_fields=('user_subscription', 'student'),
    )
    
    def __str__(self):
        return '{} - {}'.format(self.user.username, self.subscription.name)
    
    def save(self, *args, **kwargs):
        if not self.id:
            active_subscription = UserSubscription.objects.filter(
                user=self.user, subscription=self.subscription)
            if active_subscription:
                for acs in active_subscription:
                    acs.disable()
            # if self.subscription.days_term:
            #     if self.start_date:
            #         self.end_date = self.start_date + datetime.timedelta(days=self.subscription.days_term)
            #     else:
            #         self.end_date = datetime.datetime.now() + datetime.timedelta(days=self.subscription.days_term)
        return super().save(*args, **kwargs)
    
    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['disabled', 'user', 'subscription'], #todo: order?
                name="unique_together_users_subscriptions")
        ]

class StudentSubscription(Base):

    user_subscription = models.ForeignKey(UserSubscription, verbose_name=_('User subscription'), on_delete=models.CASCADE)
    student = models.ForeignKey(Student, verbose_name=_('Student'), on_delete=models.CASCADE)

    class Meta:
        verbose_name = _("Student subscription")
        verbose_name_plural = _("Students subscription")

    def __str__(self):
        return "{} - {} - {}".format(str(self.user_subscription.id), str(self.student.id))