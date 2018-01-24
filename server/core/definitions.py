PCE_STATES = {
    0 : "Running",
    1 : "Establishing Connection",
    2 : "Down",
    -1 : "Error: Undefined",
}

PCE_STATES_R = {v:k for k, v in PCE_STATES.items()}

MODULE_STATES = {
    0 : "Not on PCE",
    1 : "Available on PCE, Not Installed",
    2 : "Checkout in progress",
    -2 : "Error: Checkout failed",
    3 : "Available on PCE, Installed, Not Deployed",
    4 : "Available on PCE, Deploying",
    -4 : "Error: Deploy failed",
    5 : "Available on PCE, Deploy wait for admin",
    6 : "Available on PCE, Deployed",
    -99 : "Error: Undefined",
}

MODULE_STATES_R = {v:k for k, v in MODULE_STATES.items()}


JOB_STATES = {
    0 : "Unknown job id",
    1 : "Setting up launch",
    -1 : "Launch failed",
    2 : "Preprocessing",
    -2 : "Preprocess failed",
    3 : "Scheduled",
    -3 : "Schedule failed",
    4 : "Queued",
    5 : "Running",
    -5 : "Run failed",
    6 : "Postprocessing",
    7 : "Done",
    -99 : "Error: Undefined",
}

JOB_STATES_R = {v:k for k, v in JOB_STATES.items()}