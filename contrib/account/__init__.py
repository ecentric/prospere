def vote_user(user, score):
    from decimal import Decimal
    from models import UserProfiles

    profile = UserProfiles.objects.get(user = user)
    profile.mark = (profile.mark*profile.count_vote+Decimal(str(score)))/(profile.count_vote+1)
    profile.count_vote += 1
    profile.save()
