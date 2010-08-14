import simplejson

from django.core.urlresolvers import reverse
from django.shortcuts import render_to_response, get_object_or_404, redirect
from django.http import HttpResponse
from django.template import RequestContext
from django.views.decorators.csrf import csrf_exempt

from repocracy.repo.models import Repository, Status
from repocracy.repo.forms import NewRepoForm

def home(request):
    """
    Home page view. Form for entry of new repository.
    """
    form = NewRepoForm(request.POST or None)

    if request.POST:
        if form.is_valid():
            repo = form.save()
            return redirect(repo)

    return render_to_response('home.html', {
            'form': form
        }, context_instance=RequestContext(request))

def repo_detail(request, name):
    """
    Repository detail view. Renders `repo_pending.html` or
    `repo_detail.html` depending on status.
    """
    repo = get_object_or_404(Repository.objects.all(), slug=name)

    # TODO: better status checking?
    if Status.is_pending(repo):
        return render_to_response(
            'repo_pending.html',
            {'repo':repo},
            context_instance=RequestContext(request))

    return render_to_response('repo_detail.html', {
        }, context_instance=RequestContext(request))

def repo_claim(request, pk, claim_hash):
    if request.user.is_authenticated():
        repo = get_object_or_404(Repository, pk=int(pk), claim_hash=claim_hash, user__pk__isnull=True)
        repo.user = request.user
        repo.save()
        return redirect(repo)
    return redirect('home')

@csrf_exempt
def post_receive(request, pk):
    """
    Post-receive hook for Github/Bitbucket/whatever.
    """
    repo = get_object_or_404(Repository, pk=pk)
    repo.update()
    return HttpResponse()
