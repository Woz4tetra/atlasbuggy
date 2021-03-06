import asyncio


def wrap_iter(iterable):
    if iterable is not None:
        try:
            iter(iterable)
        except TypeError:
            iterable = (iterable,)

    return iterable


class Subscription:
    def __init__(self, tag, requested_service, is_required, expected_message_types, expected_producer_classes, queue_size,
                 error_on_full_queue, required_attributes, required_methods, callback, callback_args):
        self.tag = tag
        self.enabled = True
        self.requested_service = requested_service
        self.expected_message_types = expected_message_types
        self.expected_producer_classes = expected_producer_classes
        self.queue_size = queue_size
        self.error_on_full_queue = error_on_full_queue
        self.required_attributes = required_attributes
        self.required_methods = required_methods
        self.callback = callback
        self.callback_args = callback_args

        if self.callback is not None and not callable(self.callback):
            raise ValueError("Object '%s' is not a function." % self.callback)
        if self.callback_args is not None and type(self.callback_args) != tuple:
            raise ValueError("Callback args is not a tuple: '%s'" % self.callback_args)

        self.producer_node = None
        self.consumer_node = None
        self.queue = None
        self.message_converter = None
        self.is_required = is_required

        self.expected_message_types = wrap_iter(self.expected_message_types)
        self.expected_producer_classes = wrap_iter(self.expected_producer_classes)

    def set_nodes(self, producer, consumer):
        self.producer_node = producer
        self.consumer_node = consumer

    def check_subscription(self):
        if self.is_required:
            if self.producer_node is None or self.consumer_node is None:
                raise ValueError("Subscription '%s' not applied!! "
                                 "Please call subscribe() in your orchestrator class" % self)

    def set_event_loop(self, event_loop):
        if self.queue_size is not None:
            self.queue = asyncio.Queue(self.queue_size, loop=event_loop)

    @asyncio.coroutine
    def broadcast(self, message):
        yield from self.queue.put(message)

    def get_queue(self):
        self.check_subscription()
        if self.queue is None:
            raise ValueError("The subscription '%s' was defined to not have a queue!" % self)
        return self.queue

    def get_producer(self):
        self.check_subscription()
        return self.producer_node

    def __str__(self):
        return "%s<tag=%s, service=%s, enabled=%s, consumer=%s, producer=%s>" % (
            self.__class__.__name__, self.tag, self.requested_service, self.enabled, self.consumer_node, self.producer_node
        )
