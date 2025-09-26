from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
	USER_TYPES_CHOICES = {
		('player', 'Jogador'),
		('master', 'Mestre'),
	}

	user_type = models.CharField(
		max_length=10,
		choices=USER_TYPES_CHOICES,
			default='player'	
		
	)

	bio= models.TextField(blank=True, null=True)
	created_at = models.DateField(auto_now_add=True)
	updated_at= models.DateField(auto_now=True)

	def __str__(self):
		return f"{self.username} ({self.get_user_type_display()})"