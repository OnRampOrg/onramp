Working with Module and Job State
=================================

Module and Job state are accessed, updated, and stored using the ModState and JobState classes given in PCE.tools.modules and PCE.tools.jobs. These classes inherit from Python dictionaries, and state attrs are accessed/stored as key/value pairs of an instance. For example, to update the state of a job tracked by the instance job1::

    job1['state'] = 'New state'

Behind the scenes, state must be stored and should also be prevented from being accessed concurrently. For these reasons, ModState and JobState instances should only be accessed in conjunction with Python's with keyword. For example::

    with JobState(1) as job1:
        job1['state'] = 'New state'

Using the state classes in this manner will ensure that state files are opened/closed and state locks are acquired/released when appropriate. Note that due to the locking requirement, instantiating a state object may block if a lock is held somewhere else until it is released. To prevent deadlock when both job and module state is needed, always nest the instantiation of module state in the with block that instantiates job state. More simply, acquire job state prior to acquiring module state. For example::

    with JobState(1) as job_state:
        with ModState(27) as mod_state:
            job_state['mod_id'] = mod_state['id']

Simultaneous access to multiple JobState instances or to multiple ModState instances should not be a requirement, and thus, should be avoided. In the event that it is not avoided, a similar convention will be required to prevent deadlock (lower id first maybe?).

Locking of state instances is currently accomplished by locking their underlying state files and keeping them open for the duration of the instances' lives.
