## CUSTOM LOOKUP LAMBDA FUNCTION
The Python script , [AWS Lambda](https://aws.amazon.com/lambda/) function and [AWS CloudFormation](https://aws.amazon.com/cloudformation/) templates
described queries [Amazon DynamoDB](https://aws.amazon.com/dynamodb/) table with
the inputs from [AWS CloudFormation](https://aws.amazon.com/cloudformation/)
to lookup the mappings.

For more details refer the blog [here](https://aws.amazon.com/blogs/devops/custom-lookup-using-aws-lambda-and-amazon-dynamodb/)

## Use virtualenv for Python execution

To prevent any problems with your system Python version conflicting with the application, virtualenv can be used.

Install Python:
    `pip install python 2.7`

Install virtualenv:

    $ pip install virtualenv
    $ virtualenv -p PATH_TO_YOUR_PYTHON_2.7 venv2
    $ virtualenv ~/.virtualenvs/venv2
    $ source ~/.virtualenvs/venv2/bin/activate
    $ pip install awscli