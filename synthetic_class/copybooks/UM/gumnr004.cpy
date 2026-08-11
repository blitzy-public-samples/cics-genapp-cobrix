******************************************************************
*  COPYBOOK  : GUMNR001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Umbrella and Excess Liability (UM)
*  STATE     : MN
******************************************************************
 01  RT-UMN-RATING.

          03 RT-UMN-TERRITORY-CODE            PIC X(3).
          03 RT-UMN-CLASS-CODE                PIC X(4).
          03 RT-UMN-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-UMN-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-UMN-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-UMN-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-UMN-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-UMN-RATED-PREMIUM             PIC 9(9)V9(2).
