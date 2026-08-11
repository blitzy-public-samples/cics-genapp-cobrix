******************************************************************
*  COPYBOOK  : GFGAR001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Damage to Premises Rented to You (Fire Legal Liability) (FL)
*  STATE     : GA
******************************************************************
 01  RT-FGA-RATING.

          03 RT-FGA-TERRITORY-CODE            PIC X(3).
          03 RT-FGA-CLASS-CODE                PIC X(4).
          03 RT-FGA-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-FGA-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-FGA-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-FGA-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-FGA-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-FGA-RATED-PREMIUM             PIC 9(9)V9(2).
