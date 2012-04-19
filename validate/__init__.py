from webob.exc import HTTPPreconditionFailed

class Validate(object):

    def __init__(self, params):
        for key, value in params.items():
            setattr(self, key, value)

    def _missing(self, attr_list ):
        missing = []
        for attr in attr_list:
            if not attr in self.__dict__:
                missing.append( attr )

        if len(missing):
            return self.abort("POST fields are missing (%s) " % ",".join(missing))

    def _empty(self, attr_list ):
        empty = []
        for attr in attr_list:
            content = self.__dict__[attr].strip(' ')
            if content == "":
                empty.append( attr )

        if len(empty):
            return self.abort("POST fields are empty (%s) " % ",".join(empty))

    def validate(self, params, conditions):
        if not isinstance(params, list):
           params = list([params])

        for name in params:
            try:
                value = self.__dict__[name]
                print "Key ", name
                print "value ", value
            except KeyError:
                # Skip parameter that don't exist
                continue

            try:
                for cond in conditions:
                    if cond[1](value):
                        self.abort(cond[0] % locals())
            except ValueError:
                self.abort(cond[0] % locals())


    def abort(self, msg):
        """ Override this if method you are not using WebOb """
        raise HTTPPreconditionFailed(msg)

    def required(self, attr_list):
        # Are any of the required fields missing?
        self._missing(attr_list)
        # Are any empty?
        self._empty(attr_list)

    def only(self, attr_list):
        for value in self.__dict__:
            if not value in attr_list:
                self.abort("Parameter '%s' is not allowed, Acceptabled parameters are (%s) " % \
                    (value, ",".join(attr_list) ) )

    def allowed( self, attr, values ):
        # Ignore attributes that don't exist in the post
        # Use Post.required() for this
        if not attr in self.__dict__:
            return True

        # For each of the authorized values
        for value in values:
            # If any value matches the key
            if self.__dict__[attr] == value:
                return True
        return self.abort("Invalid %s='%s' Acceptable values are (%s) " % \
                (attr, self.__dict__[attr], ",".join(values) ) )


if __name__ == "__main__":
    post = Validate({})

    # Only these parameters are allowed, all others will result in error
    post.only(['type', 'size', 'backup_id'])

    # 'type' parameter will only accept the following values
    post.allowed('type', ['vtype', 'mytype'])

    # These parameters are required
    post.required(['size', 'backup_id'])

    # Validate the size parameter according to some conditions
    post.validate('size', [
        ["%(name) must be an integer", int],
        ["%(name) cannot be negative", lambda i: i < 0 ],
        ["%(name) cannot exceed max value", lambda i: i > 1024 ]
    ])

