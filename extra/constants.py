# ___ USER AGENT ___ #
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"


# EXPLORERS
SEPOLIA_EXPLORER = "https://sepolia.etherscan.io/tx/"
BASE_EXPLORER = "https://basescan.org/tx/"

# ID
PRIVY_APP_ID = "clphlvsh3034xjw0fvs59mrdc"


# API DEFORM QUERIES
USER_INFO = {
    "operationName": "UserMe",
    "variables": {"campaignId": "76ca585d-9554-4fc3-96c9-52e99ff93f5f"},
    "query": "fragment RecordFields on CampaignSpot {\n  records {\n    id\n    status\n    properties\n    points\n    instanceCount\n    createdAt\n    updatedAt\n    activityId\n    activity {\n      id\n      title\n      description\n      type\n      __typename\n    }\n    mission {\n      id\n      title\n      description\n      __typename\n    }\n    communityGoal {\n      id\n      title\n      description\n      threshold\n      __typename\n    }\n    rewardRecords {\n      id\n      status\n      appliedRewardType\n      appliedRewardQuantity\n      appliedRewardMetadata\n      error\n      rewardId\n      reward {\n        id\n        quantity\n        type\n        properties\n        __typename\n      }\n      __typename\n    }\n    __typename\n  }\n  __typename\n}\n\nquery UserMe($campaignId: String!) {\n  userMe {\n    id\n    campaignSpot(campaignId: $campaignId) {\n      id\n      points\n      referralCode\n      referralCodeEditsRemaining\n      ...RecordFields\n      __typename\n    }\n    __typename\n  }\n}",
}

ALL_TASKS_INFO = {
    "operationName": "Campaign",
    "variables": {"campaignId": "76ca585d-9554-4fc3-96c9-52e99ff93f5f"},
    "query": "fragment ActivityFields on CampaignActivity {\n  id\n  createdAt\n  updatedAt\n  startDateTimeAt\n  endDateTimeAt\n  title\n  description\n  coverAssetUrl\n  type\n  identityType\n  recurringPeriod {\n    count\n    type\n    __typename\n  }\n  recurringMaxCount\n  properties\n  records {\n    id\n    status\n    createdAt\n    activityId\n    properties\n    rewardRecords {\n      id\n      status\n      appliedRewardType\n      appliedRewardQuantity\n      appliedRewardMetadata\n      error\n      rewardId\n      reward {\n        id\n        quantity\n        type\n        properties\n        __typename\n      }\n      __typename\n    }\n    __typename\n  }\n  tags {\n    id\n    name\n    __typename\n  }\n  reward {\n    id\n    title\n    description\n    quantity\n    type\n    imageUrl\n    properties\n    __typename\n  }\n  targetReward {\n    id\n    activityId\n    missionId\n    __typename\n  }\n  nft {\n    id\n    tokenId\n    name\n    description\n    image\n    properties\n    mintPrice\n    platformFee\n    maxSupply\n    maxMintCountPerAddress\n    nftContract {\n      id\n      address\n      type\n      chainId\n      __typename\n    }\n    __typename\n  }\n  isHidden\n  __typename\n}\n\nfragment MissionFields on CampaignMission {\n  id\n  createdAt\n  updatedAt\n  startDateTimeAt\n  endDateTimeAt\n  title\n  description\n  coverPhotoUrl\n  recurringPeriod {\n    count\n    type\n    __typename\n  }\n  recurringMaxCount\n  properties\n  tags {\n    id\n    name\n    __typename\n  }\n  rewards {\n    id\n    title\n    description\n    quantity\n    type\n    imageUrl\n    properties\n    awardMechanism\n    __typename\n  }\n  records {\n    id\n    status\n    createdAt\n    missionId\n    rewardRecords {\n      id\n      status\n      appliedRewardType\n      appliedRewardQuantity\n      appliedRewardMetadata\n      error\n      rewardId\n      reward {\n        id\n        quantity\n        type\n        properties\n        __typename\n      }\n      __typename\n    }\n    __typename\n  }\n  activities {\n    id\n    __typename\n  }\n  isHidden\n  __typename\n}\n\nfragment CampaignCommunityGoalFields on CampaignCommunityGoal {\n  id\n  title\n  description\n  additionalDetails\n  imageUrl\n  threshold\n  status\n  startDateTimeAt\n  endDateTimeAt\n  createdAt\n  updatedAt\n  isThresholdHidden\n  isHidden\n  ctaButtonCopy\n  ctaButtonUrl\n  __typename\n}\n\nquery Campaign($campaignId: String!) {\n  campaign(id: $campaignId) {\n    activities {\n      ...ActivityFields\n      __typename\n    }\n    missions {\n      ...MissionFields\n      __typename\n    }\n    communityGoals {\n      ...CampaignCommunityGoalFields\n      activity {\n        ...ActivityFields\n        __typename\n      }\n      __typename\n    }\n    __typename\n  }\n}",
}

# TASKS QUERIES
LIKE_OUR_X_POST = {
    "operationName": "VerifyActivity",
    "variables": {"data": {"activityId": "ef348b9f-20b1-41f7-929d-09d4f163cc0d"}},
    "query": "mutation VerifyActivity($data: VerifyActivityInput!) {\n  verifyActivity(data: $data) {\n    record {\n      id\n      activityId\n      status\n      properties\n      createdAt\n      rewardRecords {\n        id\n        status\n        appliedRewardType\n        appliedRewardQuantity\n        appliedRewardMetadata\n        error\n        rewardId\n        reward {\n          id\n          quantity\n          type\n          properties\n          __typename\n        }\n        __typename\n      }\n      __typename\n    }\n    missionRecord {\n      id\n      missionId\n      status\n      createdAt\n      rewardRecords {\n        id\n        status\n        appliedRewardType\n        appliedRewardQuantity\n        appliedRewardMetadata\n        error\n        rewardId\n        reward {\n          id\n          quantity\n          type\n          properties\n          __typename\n        }\n        __typename\n      }\n      __typename\n    }\n    __typename\n  }\n}",
}


LIKE_OUR_X_POST_ABOUT_PANORAMIC_GOVERNANCE = {
    "operationName": "VerifyActivity",
    "variables": {"data": {"activityId": "20ceefde-704d-42eb-9050-7761b73d8a8f"}},
    "query": "mutation VerifyActivity($data: VerifyActivityInput!) {\n  verifyActivity(data: $data) {\n    record {\n      id\n      activityId\n      status\n      properties\n      createdAt\n      rewardRecords {\n        id\n        status\n        appliedRewardType\n        appliedRewardQuantity\n        appliedRewardMetadata\n        error\n        rewardId\n        reward {\n          id\n          quantity\n          type\n          properties\n          __typename\n        }\n        __typename\n      }\n      __typename\n    }\n    missionRecord {\n      id\n      missionId\n      status\n      createdAt\n      rewardRecords {\n        id\n        status\n        appliedRewardType\n        appliedRewardQuantity\n        appliedRewardMetadata\n        error\n        rewardId\n        reward {\n          id\n          quantity\n          type\n          properties\n          __typename\n        }\n        __typename\n      }\n      __typename\n    }\n    __typename\n  }\n}",
}

LEARN_MORE_ABOUT_ABSTRACT = {
    "operationName": "VerifyActivity",
    "variables": {"data": {"activityId": "e592f55e-db74-418b-8fe1-cef20fd8f90a"}},
    "query": "mutation VerifyActivity($data: VerifyActivityInput!) {\n  verifyActivity(data: $data) {\n    record {\n      id\n      activityId\n      status\n      properties\n      createdAt\n      rewardRecords {\n        id\n        status\n        appliedRewardType\n        appliedRewardQuantity\n        appliedRewardMetadata\n        error\n        rewardId\n        reward {\n          id\n          quantity\n          type\n          properties\n          __typename\n        }\n        __typename\n      }\n      __typename\n    }\n    missionRecord {\n      id\n      missionId\n      status\n      createdAt\n      rewardRecords {\n        id\n        status\n        appliedRewardType\n        appliedRewardQuantity\n        appliedRewardMetadata\n        error\n        rewardId\n        reward {\n          id\n          quantity\n          type\n          properties\n          __typename\n        }\n        __typename\n      }\n      __typename\n    }\n    __typename\n  }\n}",
}


FOLLOW_ABSTRACT_ON_X = {
    "operationName": "VerifyActivity",
    "variables": {"data": {"activityId": "0c08e781-93ec-4357-b1bb-eee0db23230c"}},
    "query": "mutation VerifyActivity($data: VerifyActivityInput!) {\n  verifyActivity(data: $data) {\n    record {\n      id\n      activityId\n      status\n      properties\n      createdAt\n      rewardRecords {\n        id\n        status\n        appliedRewardType\n        appliedRewardQuantity\n        appliedRewardMetadata\n        error\n        rewardId\n        reward {\n          id\n          quantity\n          type\n          properties\n          __typename\n        }\n        __typename\n      }\n      __typename\n    }\n    missionRecord {\n      id\n      missionId\n      status\n      createdAt\n      rewardRecords {\n        id\n        status\n        appliedRewardType\n        appliedRewardQuantity\n        appliedRewardMetadata\n        error\n        rewardId\n        reward {\n          id\n          quantity\n          type\n          properties\n          __typename\n        }\n        __typename\n      }\n      __typename\n    }\n    __typename\n  }\n}",
}

REPOST_OUR_X_POST_ABOUT_PANORAMIC_GOVERNANCE = {
    "operationName": "VerifyActivity",
    "variables": {"data": {"activityId": "04b177a6-0f1b-415b-8fd2-511e3ab6d612"}},
    "query": "mutation VerifyActivity($data: VerifyActivityInput!) {\n  verifyActivity(data: $data) {\n    record {\n      id\n      activityId\n      status\n      properties\n      createdAt\n      rewardRecords {\n        id\n        status\n        appliedRewardType\n        appliedRewardQuantity\n        appliedRewardMetadata\n        error\n        rewardId\n        reward {\n          id\n          quantity\n          type\n          properties\n          __typename\n        }\n        __typename\n      }\n      __typename\n    }\n    missionRecord {\n      id\n      missionId\n      status\n      createdAt\n      rewardRecords {\n        id\n        status\n        appliedRewardType\n        appliedRewardQuantity\n        appliedRewardMetadata\n        error\n        rewardId\n        reward {\n          id\n          quantity\n          type\n          properties\n          __typename\n        }\n        __typename\n      }\n      __typename\n    }\n    __typename\n  }\n}",
}

LIKE_POST_AND_LEARN_NEXT_ABOUT_ABSTRACT = {
    "operationName": "VerifyActivity",
    "variables": {"data": {"activityId": "3bfd124f-6d48-4ad5-8329-583c47d1f410"}},
    "query": "mutation VerifyActivity($data: VerifyActivityInput!) {\n  verifyActivity(data: $data) {\n    record {\n      id\n      activityId\n      status\n      properties\n      createdAt\n      rewardRecords {\n        id\n        status\n        appliedRewardType\n        appliedRewardQuantity\n        appliedRewardMetadata\n        error\n        rewardId\n        reward {\n          id\n          quantity\n          type\n          properties\n          __typename\n        }\n        __typename\n      }\n      __typename\n    }\n    missionRecord {\n      id\n      missionId\n      status\n      createdAt\n      rewardRecords {\n        id\n        status\n        appliedRewardType\n        appliedRewardQuantity\n        appliedRewardMetadata\n        error\n        rewardId\n        reward {\n          id\n          quantity\n          type\n          properties\n          __typename\n        }\n        __typename\n      }\n      __typename\n    }\n    __typename\n  }\n}",
}

LIKE_OUR_X_POST_ABOUT_OCTOBER_RECAP = {
    "operationName": "VerifyActivity",
    "variables": {"data": {"activityId": "590d6bb9-1ba8-4e57-9084-a666520a7436"}},
    "query": "mutation VerifyActivity($data: VerifyActivityInput!) {\n  verifyActivity(data: $data) {\n    record {\n      id\n      activityId\n      status\n      properties\n      createdAt\n      rewardRecords {\n        id\n        status\n        appliedRewardType\n        appliedRewardQuantity\n        appliedRewardMetadata\n        error\n        rewardId\n        reward {\n          id\n          quantity\n          type\n          properties\n          __typename\n        }\n        __typename\n      }\n      __typename\n    }\n    missionRecord {\n      id\n      missionId\n      status\n      createdAt\n      rewardRecords {\n        id\n        status\n        appliedRewardType\n        appliedRewardQuantity\n        appliedRewardMetadata\n        error\n        rewardId\n        reward {\n          id\n          quantity\n          type\n          properties\n          __typename\n        }\n        __typename\n      }\n      __typename\n    }\n    __typename\n  }\n}",
}


def get_verify_activity_json(referral_code: str = None) -> dict:
    return {
        "operationName": "VerifyActivity",
        "variables": {
            "data": {
                "activityId": "ff4d031f-c16b-4137-8cac-efc8983771e5",
                "metadata": {
                    "referralCode": referral_code,
                },
            },
        },
        "query": "mutation VerifyActivity($data: VerifyActivityInput!) {\n  verifyActivity(data: $data) {\n    record {\n      id\n      activityId\n      status\n      properties\n      createdAt\n      rewardRecords {\n        id\n        status\n        appliedRewardType\n        appliedRewardQuantity\n        appliedRewardMetadata\n        error\n        rewardId\n        reward {\n          id\n          quantity\n          type\n          properties\n          __typename\n        }\n        __typename\n      }\n      __typename\n    }\n    missionRecord {\n      id\n      missionId\n      status\n      createdAt\n      rewardRecords {\n        id\n        status\n        appliedRewardType\n        appliedRewardQuantity\n        appliedRewardMetadata\n        error\n        rewardId\n        reward {\n          id\n          quantity\n          type\n          properties\n          __typename\n        }\n        __typename\n      }\n      __typename\n    }\n    __typename\n  }\n}",
    }


def get_verify_nft_mint_json(nft_tx_hash: str, num_mints: int) -> dict:
    return {
        "operationName": "VerifyActivity",
        "variables": {
            "data": {
                "activityId": "b8b1d7ac-a807-49e6-8674-76ee72266f13",
                "metadata": {
                    "network": "base-mainnet",
                    "txHash": nft_tx_hash,
                    "numMints": num_mints,
                },
            }
        },
        "query": "mutation VerifyActivity($data: VerifyActivityInput!) {\n  verifyActivity(data: $data) {\n    record {\n      id\n      activityId\n      status\n      properties\n      createdAt\n      rewardRecords {\n        id\n        status\n        appliedRewardType\n        appliedRewardQuantity\n        appliedRewardMetadata\n        error\n        rewardId\n        reward {\n          id\n          quantity\n          type\n          properties\n          __typename\n        }\n        __typename\n      }\n      __typename\n    }\n    missionRecord {\n      id\n      missionId\n      status\n      createdAt\n      rewardRecords {\n        id\n        status\n        appliedRewardType\n        appliedRewardQuantity\n        appliedRewardMetadata\n        error\n        rewardId\n        reward {\n          id\n          quantity\n          type\n          properties\n          __typename\n        }\n        __typename\n      }\n      __typename\n    }\n    __typename\n  }\n}",
    }
