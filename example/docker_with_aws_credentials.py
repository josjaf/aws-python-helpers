import newport_helpers

NPH = newport_helpers.NPH()



def main():
    env = {'test': 'yes'}
    aws_credentials = NPH.AWSCredentialHelpers.get_credentials()
    combine = {**env, **aws_credentials}
    print(combine)
    run = NPH.Docker_Helpers.run_docker(environment_variables=combine, image_name='newport-helpers', container_name='newport-helpers-example')

    return

if __name__ == '__main__':
    main()