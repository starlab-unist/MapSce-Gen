from Utils.tools import set_environ
set_environ()


if __name__ == '__main__':
    from Utils.arguments import get_arguments
    from Concretization.Complicator import complicate_seed
    from Execution.Executor import Executor
    from Evaluation.feedback import DtwEvaluator
    from Evaluation.violation import ViolationChecker

    args = get_arguments()

    while args.next_cycle():
        seed_file = args.uncovered_seed()
        # if args.fuzzing_type == "case_study":
        #     seed_file = args.study_seed()
        # else:
        #     seed_file = args.random_select_seed()
        args.set_seed(seed_file)

        while args.next_mutation():
            if args.fuzzing_type == "experiment":
                args.prepare_seed_experiment()
                print(f"[*] Complicating Driving Scenario...")
                complicate_seed(args)
                print(f"[+] Complex Scenario is Prepared!\n")

            elif args.fuzzing_type == "case_study":
                args.prepare_seed_case_study()
                print(f"[*] Complicating Driving Scenario...")
                complicate_seed(args)
                print(f"[+] Complex Scenario is Prepared!\n")

            executor = Executor(args)
            executor.all_scenario_run()
            #
            # violation = ViolationChecker(args.log_dir_list)
            # violation.calc_violation()
            # violation.print_violation()

            # feedback = DtwEvaluator(args.model_dir_list)
            # feedback.print_difference()
            #
            # args.save_evaluation(violation)
            # if violation.violated():
            #     break
