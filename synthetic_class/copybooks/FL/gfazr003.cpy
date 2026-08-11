******************************************************************
*  COPYBOOK  : GFAZR001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Damage to Premises Rented to You (Fire Legal Liability) (FL)
*  STATE     : AZ
******************************************************************
 01  RT-FAZ-RATING.

          03 RT-FAZ-TERRITORY-CODE            PIC X(3).
          03 RT-FAZ-CLASS-CODE                PIC X(4).
          03 RT-FAZ-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-FAZ-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-FAZ-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-FAZ-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-FAZ-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-FAZ-RATED-PREMIUM             PIC 9(9)V9(2).
