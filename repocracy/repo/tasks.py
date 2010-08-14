import os
import subprocess
from repo.models import Repository 

@task
def translate_repository(repo_pk):
    pass

@task
def clone_repository(repo_pk):
    try:
        repo = Repository.objects.get(pk=repo_pk) 
        destination = os.path.join(
            settings.REPOCRACY_BASE_REPO_PATH,
            repo.pk
        )
        destination_dirs = [os.path.join(destination, type) for type in ('hg', 'git')]
        for i in destination_dirs:
            os.makedirs(i)
        result = subprocess.call(
            args=['git', '--git-dir=.', 'clone', repo.origin, '.'],
            cwd=destination_dirs[1]
        )
        if result != 0:
            result = subprocess.call(
                args=['hg', 'clone', repo.origin, '.'],
                cwd=destination_dirs[0]
            )
            if result == 0: 
                repo.origin_type = 1
                repo.status = 1
            else:
                repo.status = 255
        else:
            repo.origin_type = 0
            repo.status = 1
        repo.save()
        translate_repository.delay(repo.pk)
    except Repository.DoesNotExist:
        pass