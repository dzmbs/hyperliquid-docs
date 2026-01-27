# What does "Action already expired" mean?

This error message appears if you perform an action (e.g., placing an order) and it's not accepted by the L1 within 15 seconds. This is meant to prevent against situations where your connection is unstable or the chain is congested and you would not want the action to be delayed by more than 15 seconds.&#x20;

If you still want the action to go through (e.g., in a situation where your internet connection is bad, but you still want to trade), go to the settings dropdown and check the box next to "Disable Transaction Delay Protection".&#x20;

Important: Be aware that disabling this protection may cause delayed orders to be placed after reconnection or when congestion eases. This may result in multiple order placements (if you made multiple attempts to execute an order during the delay) when you only intended for a single action to take place. As an example, placing a short order to close a long position may result in closing the long and opening a short position if multiple short orders were attempted during the delay.

<figure><img src="https://223971011-files.gitbook.io/~/files/v0/b/gitbook-x-prod.appspot.com/o/spaces%2Fjea34cXPWRf1o1Lan56O%2Fuploads%2FLpQfg3glMaGqE9m03vhN%2FScreenshot%202025-12-18%20at%204.44.11%E2%80%AFPM.png?alt=media&#x26;token=fa5b08a4-450f-448d-a72e-2062122c3f36" alt="" width="270"><figcaption></figcaption></figure>
