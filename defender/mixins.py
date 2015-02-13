from defender import utils as utils


class DefenderWatchLogin(object):
    def form_valid(self, form):
        # if the request is currently under lockout, do not proceed to the
        # login function, go directly to lockout url, do not pass go, do not
        # collect messages about this login attempt
        if utils.is_already_locked(self.request):
            return utils.lockout_response(self.request)

        # call the login function
        response = super(DefenderWatchLogin, self).form_valid(form)
        # see if the login was successful
        login_unsuccessful = (
            response and
            not response.has_header('location') and
            response.status_code != 302
        )

        # ideally make this background task, but to keep simple, keeping
        # it inline for now.
        utils.add_login_attempt_to_db(self.request, not login_unsuccessful)
        if utils.check_request(self.request, login_unsuccessful):
            return response
        return utils.lockout_response(self.request)
