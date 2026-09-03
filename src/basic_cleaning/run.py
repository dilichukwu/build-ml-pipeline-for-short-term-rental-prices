#!/usr/bin/env python
"""
Download from W&B the raw dataset and apply some basic data cleaning, exporting the result to a new artifact
"""
import argparse
import logging
import wandb
import pandas as pd

logging.basicConfig(level=logging.INFO, format="%(asctime)-15s %(message)s")
logger = logging.getLogger()


def go(args):

    run = wandb.init(job_type="basic_cleaning")
    run.config.update(args)

    # Download input artifact. This will also log that this script is using this
    logger.info("Downloading input artifact: %s", args.input_artifact)
    artifact_local_path = run.use_artifact(args.input_artifact).file()
    # particular version of the artifact
    # artifact_local_path = run.use_artifact(args.input_artifact).file()

    ######################
    # YOUR CODE HERE     #
    
    df = pd.read_csv(artifact_local_path)    

    # Drop price outliers using the configurable min/max bounds
    logger.info("Dropping price outliers outside [%s, %s]", args.min_price, args.max_price)
    idx = df['price'].between(args.min_price, args.max_price)
    df = df[idx].copy()

    # Convert last_review to a proper datetime
    logger.info("Converting last_review to datetime")
    df['last_review'] = pd.to_datetime(df['last_review'])

    # Save the cleaned data (index=False so we don't add an extra column)
    logger.info("Saving cleaned dataframe to %s", args.output_artifact)
    df.to_csv(args.output_artifact, index=False)

    # Log the cleaned artifact to W&B
    artifact = wandb.Artifact(
    args.output_artifact,
    type=args.output_type,
    description=args.output_description,)
    artifact.add_file(args.output_artifact)
    run.log_artifact(artifact)


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="A very basic data cleaning")


    parser.add_argument(
        "--input_artifact", 
        type=str,
        help="Fully-qualified name of the input artifact to be cleaned (e.g. 'sample.csv:latest')",
        required=True
    )

    parser.add_argument(
        "--output_artifact", 
        type=str, 
        help="Name for the output (cleaned) artifact to be created (e.g. 'clean_sample.csv')",
        required=True
    )

    parser.add_argument(
        "--output_type", 
        type=str, 
        help="Type of the output artifact (e.g. 'clean_sample')",
        required=True
    )

    parser.add_argument(
        "--output_description", 
        type=str,
        help="A brief description of the output artifact",
        required=True
    )

    parser.add_argument(
        "--min_price", 
        type=float,
        help="Minimum price; rows with a price below this value are dropped",
        required=True
    )

    parser.add_argument(
        "--max_price", 
        type=float,
        help="Maximum price; rows with a price above this value are dropped",
        required=True
    )

    args = parser.parse_args()
    go(args)

