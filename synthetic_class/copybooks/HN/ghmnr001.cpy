******************************************************************
*  COPYBOOK  : GHMNR001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Hired and Non-Owned Auto Liability (HN)
*  STATE     : MN
******************************************************************
 01  RT-HMN-RATING.

          03 RT-HMN-TERRITORY-CODE            PIC X(3).
          03 RT-HMN-CLASS-CODE                PIC X(4).
          03 RT-HMN-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-HMN-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-HMN-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-HMN-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-HMN-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-HMN-RATED-PREMIUM             PIC 9(9)V9(2).
