const puppeteer = require("puppeteer");
const fs = require("fs");

const address = process.argv[2]
const chain_id = Number(process.argv[3])
const project_request = process.argv[4]
const liquidity_request = process.argv[5]
const holder_request = process.argv[6]
const score_request = process.argv[7]

function sleep(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

async function fetchGraphQLData(query, variables) {
    const response = await fetch('https://api-scanner.defiyield.app/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        // Include any other headers you need to send
      },
      body: JSON.stringify({
        query,
        variables
      })
    });
  
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
  
    const data = await response.json();
    return data;
  }
  
const project_query = `
  query($address: String!, $network: Int!) {
    project(address: $address, networkId: $network) {
      inProgress
      isProxyImplementation
      proxyContractAddress
      firstTxBlock
      estimatedAnalyzingTime
      address
      network
      rektLink
      name
      contractName
      sourceCodeLink
      whitelisted
      firstTxFrom
      firstTxDate
      logo
      projectName
      projectFullName
      initialFunder
      protocol
      pairInfo {
        factory
        tokens {
          address
          name
          symbol
          score
          logo
        }
      }
      coreIssues {
        scwTitle
        scwDescription
        scwId
        issues {
          id
          impact
          description
          data
          snippet
          start
          end
          additionalData {
            title
            description
          }
          governanceInfo {
            owners {
              timelockDelay
              type
              owner
            }
            worstOwner {
              timelockDelay
              type
              owner
            }
          }
          severityChanges {
            from
            to
            reason
          }
        }
      }
      generalIssues {
        scwTitle
        scwDescription
        scwId
        issues {
          id
          confidence
          impact
          description
          snippet
          start
          end
          additionalData {
            title
            description
          }
          governanceInfo {
            owners {
              timelockDelay
              type
              owner
            }
            worstOwner {
              timelockDelay
              type
              owner
            }
          }
          severityChanges {
            from
            to
            reason
          }
        }
      }
      stats {
        percentage
        scammed
      }
      diffs {
        id
        address
        network
        name
        projectName
        score
        createdAt
      }
      proxyData {
        sourceCodeLink
        proxyOwner
        proxyIssues {
          scwTitle
          scwDescription
          scwId
          issues {
            id
            impact
            description
            snippet
            start
            end
            additionalData {
              title
              description
            }
            governanceInfo {
              owners {
                timelockDelay
                type
                owner
              }
              worstOwner {
                timelockDelay
                type
                owner
              }
            }
            severityChanges {
              from
              to
              reason
            }
          }
        }
        implementationData {
          firstTxFrom
          firstTxDate
          firstTxBlock
          name
          initialFunder
          initialFunding
        }
      }
      governance {
        visibleOwner
        proxyOwners {
          type
          owner
          timelockDelay
          timelock
          modifiable
          impact
          governance {
            proposals
            proposalMaxActions
            votingPeriod
            quorum
            threshold
            name
          }
          multisig {
            threshold
            transactionCount
            multisigOwners
          }
        }
        contractOwners {
          type
          owner
          timelockDelay
          timelock
          modifiable
          impact
          governance {
            proposals
            proposalMaxActions
            votingPeriod
            quorum
            threshold
            name
          }
          multisig {
            threshold
            transactionCount
            multisigOwners
          }
        }
        issueOwners {
          scwId
          owners {
            type
            owner
            timelockDelay
            timelock
            modifiable
            impact
            governance {
              proposals
              proposalMaxActions
              votingPeriod
              quorum
              threshold
              name
            }
            multisig {
              threshold
              transactionCount
              multisigOwners
            }
          }
        }
      }
    }
  }`;

const governanceInfo_query = `
  query($address: String!, $network: Int!) {
    governanceInfo(address: $address, network: $network) {
      snapshot {
        id name
        followers
        link
        proposalsCount
        proposalsCount7d
        votesCount
        votesCount7d
        membersCount
        strategiesCount
        proposalsActive
        proposalsFailed
        proposalsPassed
        quorum
        members {
          address
          type
        }
        strategies {
          name
          description
          additionalInfo
        }
        proposals {
          title
          state
          winningChoice
          created
          votes
          start
          end
          link
        }
        proposalsAllTime {
          successful
          date
          votesCount
        }
      }
      tally {
        id name
        followers
        link
        proposalsCount
        proposalsCount7d
        votesCount
        votesCount7d
        membersCount
        strategiesCount
        proposalsActive
        proposalsFailed
        proposalsPassed
        quorum
        members {
          address
          type
        }
        strategies {
          name
          description
          additionalInfo
        }
        proposals {
          title
          state
          winningChoice
          created
          votes
          start
          end
          link
        }
        proposalsAllTime {
          successful
          date
          votesCount
        }
      }
    }
  }`     
  
const fakeTokenDetection_query = `
  query($address: String!, $network: Int!) {
    fakeTokenDetection(address: $address, name: "", symbol: "", networkId: $network, simplified: true){
      fake
      originalTokenLink
    }
  }`

const liquidityAnalysis_query = `
  query($address: String!, $network: Int!) {
    liquidityAnalysis(address: $address, network: $network) {
      sell24h
      buy24h
      totalLiquidity
      totalLockedPercent
      totalBurnedPercent
      totalCreatorPercent
      totalUnlockedPercent
      lpHolders {
        address
        liquidityUsd
        isContract
        locker
        isVerified
        unlockDate
        percentage
        tokensAmount
        locker
      }
      liquidityPools {
        initialLiquidity {
          token
          amount
          amountUsd
        }
        liquidityDistribution {
          creator
          creatorPercentage
          locked
          lockedPercentage
          burned
          burnedPercentage
        }
        name
        source
        address
        tokens {
          price
          reserve
          reserveUsd
          symbol
          address
          logo
        }
        isAdequateLiquidityPresent
        isEnoughLiquidityLocked
        isCreatorNotContainLiquidity
        liquidityUsd
        totalWeigth
        swapFee
        owner
      }
      issues {
        scwId
        scwTitle
        scwDescription
        issues {
          impact
          id
          confidence
          description
          start
          end
          data
          snippet
          severityChanges {
            from
            reason
            to
          }
          governanceInfo {
            owners {
              type
              owner
              modifiable
              multisig {
                multisigOwners
                threshold
                transactionCount
              }
              governance {
                proposals
                proposalMaxActions
                votingPeriod
                quorum
                threshold
                name
              }
              timelockDelay
              timelock
            }
            worstOwner {
              type
              owner
              modifiable
              multisig {
                multisigOwners
                threshold
                transactionCount
              }
              governance {
                proposals
                proposalMaxActions
                votingPeriod
                quorum
                threshold
                name
              }
              timelockDelay
              timelock
            }
          }
        }
      }
    }
  }`

const holderAnalysis_query = `
  query($address: String!, $network: Int!) {
    holderAnalysis(address: $address, network: $network, includeHolderType: true) {
      topHolders {
        address
        balance
        percent
        isContract
        isVerified
      }
      lockedPercentage
      topHoldersTotal
      topHoldersTotalPercentage
      creator
      creatorBalance
      creatorBalancePercentage
      owner
      ownerBalance
      ownerBalancePercentage
      burned
      burnedPercentage
      tokenTotalSupply
      totalHolders
      issues {
        scwId
        scwTitle
        scwDescription
        issues {
          impact
          id
          confidence
          description
          start
          end
          data
          snippet
          severityChanges {
            from
            reason
            to
          }
          governanceInfo {
            owners {
              type
              owner
              modifiable
              multisig {
                multisigOwners
                threshold
                transactionCount
              }
              governance {
                proposals
                proposalMaxActions
                votingPeriod
                quorum
                threshold
                name
              }
              timelockDelay
              timelock
            }
            worstOwner {
              type
              owner
              modifiable
              multisig {
                multisigOwners
                threshold
                transactionCount
              }
              governance {
                proposals
                proposalMaxActions
                votingPeriod
                quorum
                threshold
                name
              }
              timelockDelay
              timelock
            }
          }
        }
      }
    }
  }`

const socialAnalysis_query = `
  query($address: String!, $network: Int!) {
    socialAnalysis(address: $address, network: $network) {
      isWebsiteFound
      isWebsiteAlive
      isWebsiteFound
      isAddressConnectedToWebsite
      websiteLinks
      score
      redditInfo {
        url
        subscribers
        createdAt
        positiveCount
        negativeCount
        neutralCount
      }
      telegramInfo {
        name
        messages
        createdAt
        subscribers
      }
      issues {
        scwId
        scwTitle
        scwDescription
        issues {
          id
          impact
          confidence
          description
          start
          end
          data
          snippet
          severityChanges {
            from
            reason
            to
          }
        }
      }
    }
  }`

const score_query = `
  query($address: String!, $network: Int!) {
    score(address: $address, network: $network) {
      score
      whitelisted
      exploited
      dimensionsAmount
      finalResult
      dimensions {
        score
        name
      }
    }
  }`;

const variables = {
    "address": address,
    "network": chain_id
  };

(async () => {
  let returnValue = {}
  if (project_request === "T"){
    const project_data = await fetchGraphQLData(project_query, variables);
    returnValue["project"] = project_data.data.project
  } else {
    returnValue["project"] = false
  }

  if (liquidity_request === "T"){
    const liquidityAnalysis_data = await fetchGraphQLData(liquidityAnalysis_query, variables);
    returnValue["liquidityAnalysis"] = liquidityAnalysis_data.data.liquidityAnalysis
  } else {
    returnValue["liquidityAnalysis"] = false
  }

  if (holder_request === "T"){
    const holderAnalysis_data = await fetchGraphQLData(holderAnalysis_query, variables);
    returnValue["holderAnalysis"] = holderAnalysis_data.data.holderAnalysis
  } else {
    returnValue["holderAnalysis"] = false
  }

  if (score_request === "T"){
    const score_data = await fetchGraphQLData(score_query, variables);
    returnValue["score"] = score_data.data.score
  } else {
    returnValue["score"] = false
  }

  console.log(JSON.stringify(returnValue)); // Convert the object to a JSON string and print it
  process.exit(0);
})();